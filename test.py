import boto3
from datetime import datetime
from datetime import timedelta
aws_access_key_id='ASIAR2TIYJ2XZHR7HRXV'
aws_secret_access_key='Sszra1SBY5Vb8UZUbvD1/WRpQIT5gvnhoEuqEWwy'
aws_session_token='FwoGZXIvYXdzEIr//////////wEaDDSyniX9fPkIS9lhSSLHAW9yntXKdAHsVVsrLmu6D/B6SMq8Bu+YLtVjI50N19Z81Dbj2Jvs1A6n1kFxePEhwTT6tdKEkR/mATkyh+Jus/CAvkx8B3nBZSDM/r0Pq+TtcwwcbWS73GBVHO1HtHlacLXxyfmc+FnQP7u9x0Mk1s+sF10k29SNdzTARt+JNrrYm6+SuCfcMFvPKLgimbrzuXkIHtXkXOKCTmDzwNikihpI4D7m0wVWWHHS1TgvX2EPTLTzDXCBrsJ4oQeY5j29Dt1IlzLb/ssotMOCqQYyLf39XnR8h9L2BY6stGuqQimFcEOmgzZeQIWTfDBRByX5Jr5N7/zLfwQIukdJ/w=='
# Initialize an EC2 client


client = boto3.client(service_name='cloudwatch',
                     aws_access_key_id=aws_access_key_id,
                     aws_secret_access_key=aws_secret_access_key,
                     aws_session_token = aws_session_token,
                     region_name='us-east-1')
response = client.get_metric_statistics(
    Namespace='AWS/EC2',
    Period=period,
    StartTime=start_time,
    EndTime=end_time,
    MetricName=metric,
    Statistics=statistic,
    Unit=unit,
    Dimensions=[
        {'Name': 'InstanceId', 'Value': instance_id}
    ])
# paginator = client.get_paginator('list_metrics')
# for response in paginator.paginate(Dimensions=[{'Name': 'LogGroupName'}],
#                                    MetricName='IncomingLogEvents',
#                                    Namespace='AWS/Logs'):
#     print(response['Metrics'])


print(response)
