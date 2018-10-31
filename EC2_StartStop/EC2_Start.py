# -*- coding: utf-8 -*-
import boto3

def lambda_handler(event, context):
    # Enter the region your instances are in, e.g. 'us-east-1'
    region = event['Region']
    # Enter your instances from CloudWatch constant
    instances = event['Instances']
    ec2 = boto3.client('ec2', region_name=region)

    available_instances = []

    # get stopped instances
    try:
        response = ec2.describe_instances(
            Filters=[
                        {
                        'Name': 'instance-state-name',
                        'Values': ['stopped']
                        },
                ],
            InstanceIds=instances
            )
        stopped_instances = [v['Instances'][0]['InstanceId'] for v in response['Reservations']]
    except Exception as e:
        print('failed get stopped instances: ' + str(instances))
        print(e)
        raise e

    # started your instances
    try:
        if stopped_instances:
            ec2.start_instances(InstanceIds=stopped_instances)
            print('started your instances: ' + str(instances))
        else:
            print('There are no stopped instances')
    except Exception as e:
        print('failed started your instances: ' + str(instances))
        print(e)
        raise e
