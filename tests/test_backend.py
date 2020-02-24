import unittest
import os
from mock import patch, mock

from bucketcloner.backends import Backend

class TestBackendBucket(unittest.TestCase):
    def test_list_buckets_empty_whitelist(self):
        # Needed to choose a backend (will be mocked)
        os.environ["RCLONE_CONFIG_SRC_TYPE"] = "s3"

        with patch('bucketcloner.backends.S3') as mock:
            instance = mock.return_value
            instance.list_buckets.return_value = ["foo", "bar"]

            b = Backend("", "", env_prefix="RCLONE_CONFIG_SRC")
            buckets = b.list_buckets()
            self.assertEqual(buckets, ["foo", "bar"])

    def test_list_buckets_with_whitelist(self):
        # Needed to choose a backend (will be mocked)
        os.environ["RCLONE_CONFIG_SRC_TYPE"] = "s3"
        with patch('bucketcloner.backends.S3') as mock:
            instance = mock.return_value
            instance.list_buckets.return_value = ["foo", "bar"]

            b = Backend("", "^f.*", env_prefix="RCLONE_CONFIG_SRC")
            buckets = b.list_buckets()
            self.assertEqual(buckets, ["foo"])

class TestBackendRClone(unittest.TestCase):

    def setUp(self):
        self.backend = Backend("", "")

    @mock.patch('subprocess.Popen')
    def test_rclone_returns_output_rc(self, mock_subproc_popen):
        process_mock = mock.Mock()
        attrs = {
            'returncode': '0',
        }
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        rc, output = self.backend.run_rclone("foo")

        self.assertEqual(rc, "0")
