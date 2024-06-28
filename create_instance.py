import boto3
import config

###
# This is a code that:
#   - Creates a security group
#   - Launches 9 EC2 instances of two types
#   - Creates an Application Load Balancer
#   - Creates two Target Groups for the two types of EC2 instances
#   - Registers the instances to the Target Groups
#   - Creates a listener for the Application Load Balancer
#   - Creates two different forwarding rules for the listener
###

# AWS credentials, change based on user and new session
aws_access_key_id = config.AWS_ACCESS_KEY_ID
aws_secret_access_key = config.AWS_SECRET_ACCESS_KEY
aws_session_token = config.AWS_SESSION_TOKEN
# Initialize an EC2 client
ec2 = boto3.client('ec2',
                   aws_access_key_id=aws_access_key_id,
                   aws_secret_access_key=aws_secret_access_key,
                   aws_session_token=aws_session_token,
                   region_name='us-east-1')

ec2_waiter = ec2.get_waiter('instance_running')

vpc_id = ec2.describe_vpcs()['Vpcs'][0]['VpcId']

security_group_name = config.SECURITY_GROUP_NAME

# Creates a security group
security_group = ec2.create_security_group(
    GroupName=security_group_name,
    Description='Security group for TP1 project'
)

######Comment out the following 20 rows if you created security group once
# Extracts the ARN ID for the security group
sg_id = security_group['GroupId']

# Associated with creation of security group
ec2.authorize_security_group_ingress(
    GroupId=sg_id,
    IpProtocol='tcp',
    FromPort=22,
    ToPort=22,
    CidrIp='0.0.0.0/0'
)

# Associated with creation of security group
ec2.authorize_security_group_ingress(
    GroupId=sg_id,
    IpProtocol='tcp',
    FromPort=80,
    ToPort=80,
    CidrIp='0.0.0.0/0'
)
#######Comment out until here

# If you already created a security group with the previous code use this sg_id instead, you'll find the id on AWS website
# sg_id = 'you own security id code' 

# Settings
image_id = 'ami-053b0d53c279acc90'

m4_no_instances = 5
# Launching 5 EC2 instances of type M4 Large
m4_instances = ec2.run_instances(
    ImageId=image_id,
    InstanceType='m4.large',
    MaxCount=m4_no_instances,
    MinCount=m4_no_instances,
    Placement={'AvailabilityZone': 'us-east-1a'},
    KeyName='Key-1',
    SecurityGroups=[security_group_name],
)

# Extracts list of m4 instances
m4_instances_list = m4_instances['Instances']

t2_no_instances = 4
# Launching 4 EC2 instances of type T2 Large
t2_instances = ec2.run_instances(
    ImageId=image_id,
    InstanceType='t2.large',
    MaxCount=t2_no_instances,
    MinCount=t2_no_instances,
    Placement={'AvailabilityZone': 'us-east-1b'},
    KeyName='Key-1',
    SecurityGroups=[security_group_name],
)

# Extracts list of t2 instances
t2_instances_list = t2_instances['Instances']

# Initialize the ELBv2 client
elbv2 = boto3.client('elbv2',
                     aws_access_key_id=aws_access_key_id,
                     aws_secret_access_key=aws_secret_access_key,
                     aws_session_token=aws_session_token,
                     region_name='us-east-1')

subnet1 = ec2.describe_subnets()['Subnets'][0]['SubnetId']
subnet2 = ec2.describe_subnets()['Subnets'][1]['SubnetId']

# Create a Application Load Balancer
application_load_balancer = elbv2.create_load_balancer(
    Name='T1-load-balancer',
    Type='application',
    SecurityGroups=[sg_id],
    Subnets=[  # May have to change subnets to yours, they can be found at your account at the AWS website
        subnet1,
        subnet2,
    ]
)

# Application load balancer arn
application_load_balancer_id = application_load_balancer['LoadBalancers'][0]['LoadBalancerArn']

# Create a Target Group for m4
m4_target_group = elbv2.create_target_group(
    Name='m4-target-group',
    TargetType='instance',
    Protocol='HTTP',
    ProtocolVersion='HTTP1',
    Port=80,
    VpcId=vpc_id,
    IpAddressType='ipv4'
    # HealthCheckProtocol='HTTP',
    # HealthCheckPath='/',
)

# m4 target group arn
m4_target_group_id = m4_target_group['TargetGroups'][0]['TargetGroupArn']

# Create a Target Group for t2
t2_target_group = elbv2.create_target_group(
    Name='t2-target-group',
    TargetType='instance',
    Protocol='HTTP',
    ProtocolVersion='HTTP1',
    Port=80,
    VpcId=vpc_id,
    IpAddressType='ipv4'
    # HealthCheckProtocol='HTTP',
    # HealthCheckPath='/',
)

# t2 target roup arn
t2_target_group_id = t2_target_group['TargetGroups'][0]['TargetGroupArn']

# Register instances to m4 target group
for instance in m4_instances_list:
    instance_id = instance['InstanceId']
    ec2_waiter.wait(InstanceIds=[instance_id])

    elbv2.register_targets(
        TargetGroupArn=m4_target_group_id,
        Targets=[
            {
                'Id': instance_id,
                'Port': 80,
            },
        ]
    )

# Register instances to t2 target group
for instance in t2_instances_list:
    instance_id = instance['InstanceId']
    ec2_waiter.wait(InstanceIds=[instance_id])
    elbv2.register_targets(
        TargetGroupArn=t2_target_group_id,
        Targets=[
            {
                'Id': instance_id,
                'Port': 80,
            },
        ]
    )

# Create a listener for the Application Load Balancer
listener = elbv2.create_listener(
    LoadBalancerArn=application_load_balancer_id,  # Extract the ARN from the load balancer
    Protocol='HTTP',
    Port=80,
    DefaultActions=[
        {
            'Type': 'fixed-response',
            'FixedResponseConfig': {
                'ContentType': 'text/plain',
                'StatusCode': '404',
                'MessageBody': 'Default response',
            }
        },
    ]
)

listener_arn = listener['Listeners'][0]['ListenerArn']

# Defining the conditions and actions of two rules
listener_rules = [
    {
        'RulePriority': 1,
        'Conditions': [
            {
                'Field': 'path-pattern',
                'Values': ['/cluster1']
            }
        ],
        'Actions': [
            {
                'Type': 'forward',
                'TargetGroupArn': m4_target_group_id,
            }
        ]
    },
    {
        'RulePriority': 2,
        'Conditions': [
            {
                'Field': 'path-pattern',
                'Values': ['/cluster2']
            }
        ],
        'Actions': [
            {
                'Type': 'forward',
                'TargetGroupArn': t2_target_group_id,
            }
        ]
    }
]

# Creates a rule for the listener using the defined rules above
for rule in listener_rules:
    elbv2.create_rule(
        ListenerArn=listener_arn,
        Conditions=rule['Conditions'],
        Priority=rule['RulePriority'],
        Actions=rule['Actions']
    )
