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

			auto_instrument()  # or instrument(requests=True)
			traced_session = requests.Session()
			traced_post_response = traced_session.post("http://35.236.100.236:6000/echo")
			#response = requests.post("http://35.236.100.236:6000/echo")

			print ('response->',traced_post_response)

			response['responseCode']=traced_post_response.status_code
			response['elapsedTime']=traced_post_response.elapsed.total_seconds()

		return response


def regular_request(event,context):
	response = {}
	if event['method'].upper().decode('utf-8','ignore') == 'POST':
		resp = requests.post(event['url'],headers=event['headers'],body=event['body'])
		response['responseCode']=resp.status_code
		response['elapsedTime']=resp.elapsed.total_seconds()
	elif event['method'].upper().decode('utf-8','ignore') == 'GET' or event['method'].decode('utf-8','ignore') == '':
		resp = requests.get(event['url'])
		response['responseCode']=resp.status_code
		response['elapsedTime']=resp.elapsed.total_seconds()
	else:
		response = '{"message":"Request Type is unsupported (Only GET/POST is supported)","responseCode":404,"elapsedTime":"0"}'
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

	if event['url'] == 'http://trace.com':
		testTrace = InjectTrace()
		return testTrace.trace_request(event,context)	
	else:
		return regular_request(event,context)
