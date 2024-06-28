from operator import itemgetter
from datetime import datetime, date
import json
import os
import config
import boto3

# AWS Credentials
aws_access_key_id = config.AWS_ACCESS_KEY_ID
aws_secret_access_key = config.AWS_SECRET_ACCESS_KEY
aws_session_token = config.AWS_SESSION_TOKEN
from datetime import timedelta


def json_serial(obj):
    """
    Serialize timestamps into JSON format.
    """
    if isinstance(obj, (datetime, date)):
        serial = obj.strftime("%Y-%m-%d %H:%M:%S")
        return serial
    raise TypeError("Type %s not serializable" % type(obj))


def get_all_EC2_instances(ec2_connection=None):
    """
    Return a list with all EC2 instances in a region.
    """
    response = ec2_connection.describe_instances()

    instances_reservation = response['Reservations']
    instances_description = []

    instances_id_list = []

    for reservation in instances_reservation:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            instances_id_list.append((instance_id, instance_type))
    return instances_id_list


def get_cloudwatch_metric(instance, instance_type, metric_name, cw_connection, start_time, end_time):
    """
    Return the last result of the metric passed as an argument.
    """

    response = cw_connection.get_metric_statistics(
        Period=300,
        StartTime=start_time,
        EndTime=end_time,
        MetricName=metric_name,
        Namespace='AWS/EC2',
        Statistics=['Average'],
        Dimensions=[{
            'Name': 'InstanceId',
            'Value': instance
        }]
    )['Datapoints']

    last_datapoint = sorted(response, key=itemgetter('Timestamp'))[-1]

    return last_datapoint


def get_list_of_cloudwatch_metrics_by_instance(instance, cw_connection=None):
    """
    Return a list with all CloudWatch metrics for an EC2 instance.
    """
    response = cw_connection.list_metrics(
        Namespace='AWS/EC2',
        Dimensions=[{
            'Name': 'InstanceId',
            'Value': instance
        }]
    )
    metrics_list = response['Metrics']
    metrics_names = [metric['MetricName'] for metric in metrics_list]
    return metrics_names


def cloud_watch_metrics(start_time, end_time):
    start_time = start_time - timedelta(minutes=10)

    regions = ['us-east-1']
    results_metrics_by_region = []

    for region_name in regions:
        ec2_client = boto3.client('ec2',
                                  aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key,
                                  aws_session_token=aws_session_token,
                                  region_name='us-east-1')
        cloudwatch_client = boto3.client(service_name='cloudwatch',
                                         aws_access_key_id=aws_access_key_id,
                                         aws_secret_access_key=aws_secret_access_key,
                                         aws_session_token=aws_session_token,
                                         region_name='us-east-1')

        ec2_instances = get_all_EC2_instances(ec2_connection=ec2_client)

        results_metrics_by_instance = []

        if ec2_instances:

            metrics_list = []
            for instance_id, instance_type in ec2_instances:
                instance_metric_obj = {
                    'instance_id': instance_id,
                    'instance_type': instance_type,
                    'metrics': get_list_of_cloudwatch_metrics_by_instance(
                        instance=instance_id,
                        cw_connection=cloudwatch_client)
                }

                metrics_list.append(instance_metric_obj)

            for instance in metrics_list:
                instance_obj = {}
                instance_obj['instance_id'] = instance['instance_id']
                instance_obj['instance_type'] = instance['instance_type']
                instance_obj['metrics'] = []

                for metric in instance['metrics']:
                    instance_obj['metrics'].append({
                        'name': metric,
                        'value': get_cloudwatch_metric(instance['instance_id'],
                                                       instance['instance_type'],
                                                       metric,
                                                       cloudwatch_client, start_time, end_time)
                    })

                results_metrics_by_instance.append(instance_obj)

            results_metrics_by_region.append({
                'region': region_name,
                'instances': results_metrics_by_instance
            })

    # filename = 'output.json'
    # with open(filename, 'w') as json_file:
    #     json.dump(results_metrics_by_region, json_file, default=json_serial, indent=4, separators=(',', ': '))
    print(json.dumps(results_metrics_by_region, default=json_serial,
                     indent=4, separators=(',', ': ')))
    # print(f"JSON data saved to {filename}")


if __name__ == '__main__':
    start_time = datetime.utcnow()
    end_time = datetime.utcnow()
    time.sleep(10)
    cloud_watch_metrics(start_time, end_time)
