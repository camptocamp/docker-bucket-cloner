import boto3

class S3(object):
    def __init__(self, **kwargs):
        self.s3_client = boto3.client('s3', **kwargs)

    def list_buckets(self):
        buckets = []
        for bucket in self.s3_client.list_buckets()['Buckets']:
            buckets.append(bucket['Name'])
        return buckets
