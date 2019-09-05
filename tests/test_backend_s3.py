import unittest
import boto3
from moto import mock_s3

from bucketcloner.backends import S3

class TestS3Bucket(unittest.TestCase):
    @mock_s3
    def test_list_buckets(self):
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket='foo')
        conn.create_bucket(Bucket='bar')

        backend = S3()
        buckets = backend.list_buckets()
        self.assertEqual(buckets, ["foo", "bar"])
