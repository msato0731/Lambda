import boto3
import alarm_name

def lambda_handler(event, context):
    region = 'ap-northeast-1'
    cloud_watch = boto3.client('cloudwatch', region_name=region)
    alarm_names = alarm_name.list
    cloud_watch.disable_alarm_actions(AlarmNames=alarm_names)