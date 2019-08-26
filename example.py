import json
import requests
from jaeger_client import Config
import opentracing
from opentracing.ext import tags
import signalfx_lambda
from signalfx_tracing import auto_instrument
from signalfx_tracing.libraries import requests_config 


class InjectTrace(object):

	def __init__(self):
		self.tracer = opentracing.tracer

	def handle_request(self,event,context):
		span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
		with self.tracer.start_span('handle_request', tags=span_tags) as span:
			span.set_tag('aws_request_id',context.aws_request_id)
			requests_config.propagate = True
			requests_config.tracer = self.tracer

			auto_instrument()  # or instrument(requests=True)
			traced_session = requests.Session()
			traced_post_response = traced_session.post("http://35.236.100.236:6000/echo")
			#response = requests.post("http://35.236.100.236:6000/echo")
			print ('response->',traced_post_response)
		return response

# Our registered Lambda handler entrypoint (example.request_handler) with the
# SignalFx Lambda wrapper
@signalfx_lambda.is_traced
def request_handler(event, context):
	testTrace = InjectTrace()
	testTrace.handle_request(event,context)
	return '{"message":"OK"}'
