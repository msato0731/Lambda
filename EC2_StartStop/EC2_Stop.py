# -*- coding: utf-8 -*-
import boto3

def lambda_handler(event, context):
    # Enter the region your instances are in, e.g. 'us-east-1'
    region = event['Region']
    # Enter your instances from CloudWatch constant
    instances = event['Instances']
    ec2 = boto3.client('ec2', region_name=region)

    stopped_instances = []

    # get available instances
    try:
        response = ec2.describe_instances(
            Filters=[
                        {
                        'Name': 'instance-state-name',
                        'Values': ['running']
                        },
                ],
            InstanceIds=instances
            )
        available_instances = [v['Instances'][0]['InstanceId'] for v in response['Reservations']]
    except Exception as e:
        print('failed get available instances: ' + str(instances))
        print(e)
        raise e

    # stopped your instances
    try:
        if available_instances:
            ec2.stop_instances(InstanceIds=available_instances)
            print('stopped your instances: ' + str(instances))
        else:
            print('There are no instances running')
    except Exception as e:
        print('failed stopped your instances: ' + str(instances))
        print(e)
        raise e
