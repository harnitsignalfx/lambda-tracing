# OpenTracing and Jaeger in AWS Lambda Python Runtime

This is an example of a simple, traced Lambda function using the SignalFx Lambda Wrapper and Jaeger Python tracer with SignalFx.
See [example.py](./example.py) for the example code.

## Building and creating a Deployment Package

A Python deployment package for AWS Lambda is a .zip file consisting of your application code and any dependencies.
To prepare this project and create the deployable archive follow these instructions from this document's parent
directory:

```
$ pwd  # Confirm this is <your_local_path/tracing-examples/aws-lambda/jaeger-python>
$ pip install -r requirements.txt -t .
$ find . -name "*.py[co]" -delete
$ find . -name "*.dist-info" -exec rm -r "{}" \;
$ zip -r my_traced_python_lambda.zip *
```

The resulting `my_traced_python_lambda.zip` can be uploaded to S3 or in your browser via the AWS Console
during function creation. Register your handler as `example.request_handler` and don't forget to set the
`SIGNALFX_ENDPOINT_URL` environment variable to point to your Gateway. Set
`SIGNALFX_SERVICE_NAME` to `signalfx-lambda-python-example` or something else
descriptive. You should be able test the application with the following test
event:

```
{
  "url": "https://www.signalfx.com",
  "method": "GET",
  "headers": {},
  "body": "{\"abc\":\"def\"}"
}
```

To inject a trace object to the underlying flask server, you need to set the url to be `http://trace.com`
```
{
  "url": "http://trace.com",
  "method": "POST",
  "headers": {},
  "body": "{\"abc\":\"def\"}"
}
```
