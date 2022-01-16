import logging
import handler

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - [%(levelname)s] %(message)s',
    level=logging.INFO
)
event = {
    'Records': [
        {
            'eventVersion': '2.1',
            'eventSource': 'aws:s3',
            'awsRegion': 'ap-southeast-2',
            'eventTime': '2021-12-31T11:51:00.976Z',
            'eventName': 'ObjectCreated:Put',
            'userIdentity': {
                'principalId': 'AWS:AROA6KLLTAH7UPMCB2F3T:chris@trivialsec.com'
            },
            'requestParameters': {
                'sourceIPAddress': '180.150.30.218'
            },
            'responseElements': {
                'x-amz-request-id': 'PY0VW78P539K3KXE',
                'x-amz-id-2': 'Ngoa8ePYrtuvWRONPCh95FwkwapKP9kmmyEms1O/3Fs8imumg0KAABeO9szx2d/P5vJRkV+tZlg91yTJy0AVVxko2IsKURSN'
            },
            's3': {
                's3SchemaVersion': '1.0',
                'configurationId': 'tf-s3-lambda-20211231065758685200000001',
                'bucket': {
                    'name': 'assets-trivialsec',
                    'ownerIdentity': {
                        'principalId': 'AZSHVQMG8WNFI'
                    },
                    'arn': 'arn:aws:s3:::assets-trivialsec'
                },
                'object': {
                    'key': 'metadata-service/test.queue',
                    'size': 48,
                    'eTag': 'f5e6545b7a7a14f56ef6aa4dfef8619e',
                    'versionId': 'wsqG_62tdCzpWLLfugvaZrXL.X3nDmSu',
                    'sequencer': '0061CEEEA4E6D7FEAF'
                }
            }
        }
    ]
}
context = {
    'aws_request_id': "7c21cee6-485a-4073-8134-63e340e83621",
    'log_group_name': "/aws/lambda/metadata-service",
    'log_stream_name': "2021/12/31/[$LATEST]efedd01b329b4041b660f9ce510228cc",
    'function_name': "metadata-service",
    'memory_limit_in_mb': 128,
    'function_version': "$LATEST",
    'invoked_function_arn': "arn:aws:lambda:ap-southeast-2:984310022655:function:metadata-service",
    'client_context': None,
    'identity': None
}
handler.lambda_handler(event, context)
