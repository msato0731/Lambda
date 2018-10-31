# -*- coding: utf-8 -*-
#
# 特定のタグを含むEBSボリュームのスナップショットを作成する。
#   Python 3.6
#
#   （参考）
#   https://qiita.com/HorieH/items/66bb68d12bd8fdbbd076
#   https://inaba-serverdesign.jp/blog/20180330/aws_ec2_create_snapshot_lambda.html
# EBSボリュームが存在するリージョンでLambda関数を作成すること。
#
# 対象とするボリュームのタグで、
# Key: <TAGKEYの文字列>, Value: <保存世代数>
# を設定すること。
#
TAGKEY = 'Backup-Generation'

import boto3
import collections
import time
from datetime import datetime as dt

from botocore.client import ClientError
import os

client = boto3.client('ec2', os.environ['AWS_REGION'])

def lambda_handler(event, context):
    descriptions = create_snapshots()
    delete_old_snapshots(descriptions)

def create_snapshots():
    volumes = get_volumes([TAGKEY])

    descriptions = {}

    for v in volumes:
        tags = { t['Key']: t['Value'] for t in v['Tags'] }
        generation = int( tags.get(TAGKEY, 0) )

        if generation < 1:
            continue

        volume_id = v['VolumeId']
        description = volume_id if tags.get('Name') is '' else '%s(%s)' % (volume_id, tags['Name'])
        description = 'Auto Snapshot ' + description
        snapshot = _create_snapshot(volume_id, description)
        snapshot_id = snapshot['SnapshotId']
        snapshot_name = get_snapshot_name(volume_id)
        print(snapshot_name)
        _create_tags(snapshot_id,snapshot_name)
        print('create snapshot %s(%s)' % (snapshot['SnapshotId'], description))

        descriptions[description] = generation

    return descriptions

def get_volumes(tag_names):
    volumes = client.describe_volumes(
        Filters=[
            {
                'Name': 'tag-key',
                'Values': tag_names
            }
        ]
    )['Volumes']

    return volumes

def delete_old_snapshots(descriptions):
    snapshots_descriptions = get_snapshots_descriptions(list(descriptions.keys()))

    for description, snapshots in snapshots_descriptions.items():
        delete_count = len(snapshots) - descriptions[description]

        if delete_count <= 0:
            continue

        snapshots.sort(key=lambda x:x['StartTime'])

        old_snapshots = snapshots[0:delete_count]

        for s in old_snapshots:
            _delete_snapshot(s['SnapshotId'])
            print('delete snapshot %s(%s)' % (s['SnapshotId'], s['Description']))

def get_snapshots_descriptions(descriptions):
    snapshots = client.describe_snapshots(
        Filters=[
            {
                'Name': 'description',
                'Values': descriptions,
            }
        ]
    )['Snapshots']

    groups = collections.defaultdict(lambda: [])
    { groups[ s['Description'] ].append(s) for s in snapshots }

    return groups

def _create_snapshot(id, description):
    for i in range(1, 3):
        try:
           return client.create_snapshot(VolumeId=id,Description=description)
        except ClientError as e:
            print(str(e))
        time.sleep(1)
    raise Exception('cannot create snapshot ' + description)

def _delete_snapshot(id):
    for i in range(1, 3):
        try:
            return client.delete_snapshot(SnapshotId=id)
        except ClientError as e:
            print(str(e))
            if e.response['Error']['Code'] == 'InvalidSnapshot.InUse':
                return;
        time.sleep(1)
    raise Exception('cannot delete snapshot ' + id)

def _create_tags(id,name):
    response = client.create_tags(
        DryRun=False,
        Resources=[
            id ,
        ],
        Tags=[
            {
                'Key': 'Name',
                'Value': name
            },
        ]
    )
def get_snapshot_name(id):
    exec_time = dt.now().strftime('%Y%m%d')
    response = 'Seven Batch Add Volume_' + exec_time
    print(response)
    return response
# EOF
