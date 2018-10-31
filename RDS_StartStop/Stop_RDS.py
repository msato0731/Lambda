# -*- coding: utf-8 -*-
import boto3

def lambda_handler(event, context):
    # Enter the region your instances are in, e.g. 'us-east-1'
    region = event['Region']
    # Enter your instances from CloudWatch constant
    db_instance = event['Db_Instance']
    rds = boto3.client('rds', region_name=region)
    db_status = False

    # check db instance state
    try:
        response = rds.describe_db_instances(
            Filters=[
                    {'Name': 'db-instance-id',
                    'Values': [db_instance]
                    },
                ]
            )
        if response['DBInstances'][0]['DBInstanceStatus'] == 'available': db_status = True
    except Exception as e:
        print('failed check db instance state: ' + str(db_instance))
        print(e)
        raise e

    # stop your db instance
    try:
        if db_status:
            rds.stop_db_instance(DBInstanceIdentifier=db_instance)
            print('stop your db instance: ' + str(db_instance))
        else:
            print('DB is stopped')
    except Exception as e:
        print('failed stop your db instance: ' + str(db_instance))
        print(e)
        raise e
