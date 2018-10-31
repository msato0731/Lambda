# -*- coding: utf-8 -*-
import boto3
import os

# Enter region your instances are in, e.g. 'us-east-1'
region = os.environ['region']
# use SNS sender
TOPIC_ARN = os.environ['topic']
msg = ''
subject = 'RDS メンテナンス情報'
notice = False

def lambda_handler(event, context):
    rds = boto3.client('rds', region_name=region)
    global notice

# get maintenance information
    try:
        response = rds.describe_pending_maintenance_actions()
        print(response)
    except Exception as e:
        print('failed get rds maintenance_actions')
        print(e)
        raise e

# format the response for rds notification
    try:
        if len(response['PendingMaintenanceActions']) > 0:
            msg = format_rds_notification(response)
            print(msg)
            notice = True
    except Exception as e:
        print('failed form maintenance notification')
        print(e)
        raise e

# sns notification
    try:
        if notice:
            sns_notification(TOPIC_ARN, msg, subject, region)
        else:
            print('rds maintenance is none')
    except Exception as e:
        print('failed sns notification')
        print(e)
        raise e

def format_rds_notification(response):
    line_feed_code = '\n'
    messages = [
                'ご担当者各位' + (line_feed_code * 2) +
                'RDSのメンテナンス情報を通知いたします。' + line_feed_code
               ]

    MaintenanceAction_format = []
    for MaintenanceAction in response['PendingMaintenanceActions']:
        MaintenanceAction_format.append('ResourceIdentifier: ' + str(MaintenanceAction['ResourceIdentifier']))
        MaintenanceAction_format.append('-----')
        for index, PendingMaintenanceActionDetail in enumerate(MaintenanceAction['PendingMaintenanceActionDetails']):
            Action = PendingMaintenanceActionDetail['Action']
            Description = PendingMaintenanceActionDetail['Description']
            AutoAppliedAfterDate = PendingMaintenanceActionDetail['AutoAppliedAfterDate'] if 'AutoAppliedAfterDate' in PendingMaintenanceActionDetail else 'none'
            ForcedApplyDate = PendingMaintenanceActionDetail['ForcedApplyDate'] if 'ForcedApplyDate' in PendingMaintenanceActionDetail else 'none'
            OptInStatus = PendingMaintenanceActionDetail['OptInStatus'] if 'OptInStatus' in PendingMaintenanceActionDetail else 'none'
            CurrentApplyDate = PendingMaintenanceActionDetail['CurrentApplyDate'] if 'CurrentApplyDate' in PendingMaintenanceActionDetail else 'none'

            if index >= 1 : MaintenanceAction_format.append('')
            MaintenanceAction_format.append(
                                            'Action: ' + str(Action) + line_feed_code +
                                            'Description: ' + str(Description) + line_feed_code +
                                            'AutoAppliedAfterDate: ' + str(AutoAppliedAfterDate) + line_feed_code +
                                            'ForcedApplyDate: ' + str(ForcedApplyDate) + line_feed_code +
                                            'OptInStatus: ' + str(OptInStatus) + line_feed_code +
                                            'CurrentApplyDate: ' + str(CurrentApplyDate)
                                           )

        MaintenanceAction_format.append('-----' + line_feed_code)
    messages.append(','.join(MaintenanceAction_format) + line_feed_code +
                    '以上、ご確認よろしくお願いいたします。'
                   )
    msg = ','.join(messages).replace(',', line_feed_code)

    return msg

def sns_notification(TOPIC_ARN, msg, subject, region):
    sns = boto3.client('sns', region_name=region)

    request = {
        'TopicArn': TOPIC_ARN,
        'Message': msg,
        'Subject' : subject
    }

    response = sns.publish(**request)
    print(response)
