import boto3
 
# Connect to the EC2 service
ec2 = boto3.client('ec2',
                   'ap-south-1',
                   aws_access_key_id='',
                   aws_secret_access_key='')
 
# Terminate the instance with the specified ID
response = ec2.terminate_instances(InstanceIds=['instance-id-1'])
 
# Print the response
print(response)