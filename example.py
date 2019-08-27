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

	def trace_request(self,event,context):
		response = {}
		span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
		with self.tracer.start_span('trace_request', tags=span_tags) as span:
			span.set_tag('aws_request_id',context.aws_request_id)
			requests_config.propagate = True
			requests_config.tracer = self.tracer

			auto_instrument()
			traced_session = requests.Session()

			#traced_post_response = traced_session.post("http://35.236.100.236:6000/echo")

			response = {}
			if event['method'].upper().decode('utf-8','ignore') == 'POST':
				resp = traced_session.post(event['url'],headers=event['headers'],body=event['body'])
				response['responseCode']=resp.status_code
				response['elapsedTime']=resp.elapsed.total_seconds()*1000
			elif event['method'].upper().decode('utf-8','ignore') == 'GET' or event['method'].decode('utf-8','ignore') == '':
				resp = traced_session.get(event['url'])
				response['responseCode']=resp.status_code
				response['elapsedTime']=resp.elapsed.total_seconds()*1000
			else:
				response = '{"error":true}'

		return response



# Our registered Lambda handler entrypoint (example.request_handler) with the
# SignalFx Lambda wrapper
@signalfx_lambda.is_traced
def request_handler(event, context):
	if not 'url' in event:
		return '{"message":"Url missing"}',500
	if not 'method' in event:
		return '{"message":"method type GET/PUT etc is missing"}',500
	if not 'headers' in event:
		return '{"message":"Headers are missing"}',500
	if not 'body' in event:
		return '{"message":"Message body is missing"}',500

	
	testTrace = InjectTrace()
	return testTrace.trace_request(event,context)	
