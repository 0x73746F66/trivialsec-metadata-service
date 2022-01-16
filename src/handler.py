import json
import logging
from datetime import datetime
import boto3
import tlsverify

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    logger.info(f'Reading {file_key} from {bucket_name}')
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    input_data = json.loads(obj.get('Body', '').read().strip())
    domain_name = input_data['domain']
    port = input_data.get('port', 443)
    logger.info(f'target: {domain_name}:{port}')
    evaluation_start = datetime.utcnow()
    _, results = tlsverify.verify(host = domain_name, port = port)
    tls_data = tlsverify.to_dict(results, (datetime.utcnow() - evaluation_start).total_seconds())
    s3.put_object(Bucket=bucket_name, Key=f'metadata-service/{domain_name}/tls-verify/{input_data["job_uuid"]}.json', Body=json.dumps(tls_data, default=str, sort_keys=True))

    input_data['timings']['completed_at'] = datetime.utcnow().replace(microsecond=0).isoformat()
    input_data['report_summary'] = "done"
    s3.put_object(Bucket=bucket_name, Key=file_key, Body=json.dumps(input_data, default=str, sort_keys=True))
