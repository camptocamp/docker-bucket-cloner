import os
import re
import sys
import time
import logging
import subprocess
from prometheus_client import Gauge

from .s3 import S3
from .swift import Swift


class Backend(object):
    def __init__(self, destination_pattern, whitelist, env_prefix=""):
        self.whitelist = whitelist or ""
        self.destination_pattern = destination_pattern
        self.metrics = {
                'rclone_start_time': Gauge(
                    "rclone_start_time",
                    "When RClone started.",
                    ["source", "destination"]),
                'rclone_end_time': Gauge(
                    "rclone_end_time",
                    "When RClone stopped.",
                    ["source", "destination"]),
                'rclone_rc': Gauge(
                    "rclone_rc",
                    "Return code from RClone.",
                    ["source", "destination"]),
                'rclone_errors': Gauge(
                    "rclone_errors",
                    "Errors from RClone.",
                    ["source", "destination"]),
                }

        if env_prefix != "":
            objstorage_type = os.environ.get("{}_TYPE".format(env_prefix))
            if objstorage_type == "s3":
                self.backend = S3(
                    aws_access_key_id=os.environ.get("{}_ACCESS_KEY_ID".format(env_prefix)),
                    aws_secret_access_key=os.environ.get("{}_SECRET_ACCESS_KEY".format(env_prefix)),
                    endpoint_url=os.environ.get("{}_ENDPOINT".format(env_prefix)))
            elif objstorage_type == "swift":
                self.backend = Swift(
                    user=os.environ.get("{}_USER".format(env_prefix)),
                    key=os.environ.get("{}_KEY".format(env_prefix)),
                    tenant_name=os.environ.get("{}_TENANT".format(env_prefix)),
                    os_options={
                        "region_name": os.environ.get("{}_REGION".format(env_prefix)),
                    },
                    auth_version=os.environ.get("{}_AUTH_VERSION".format(env_prefix), "3"),
                    authurl=os.environ.get("{}_AUTH".format(env_prefix)))
            else:
                raise ValueError("unsupported value for {}_TYPE".format(env_prefix))
        else:
            logging.warning("no backend has been initialized because no `env_prefix` provided.")

    def list_buckets(self):
        buckets = []
        raw_buckets = self.backend.list_buckets()
        for rb in raw_buckets:
            ro = re.compile(self.whitelist)
            if ro.match(rb):
                buckets.append(rb)
        return buckets

    def run_rclone(self, bucket):
        destination_bucket = self.destination_pattern.replace("[bucket]", bucket)
        logging.info(destination_bucket)

        start_time = time.time()

        popen = subprocess.Popen(['rclone', '-v', 'sync',
            '--s3-acl', 'private',
            'src:{}'.format(bucket),
            'dst:{}'.format(destination_bucket)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1, universal_newlines=True)

        rclone_errors = 0
        # Poll process for new output until finished
        for line in popen.stdout:

            # Check for errors
            match_rclone_errors = re.findall(r'Errors:\s+(\d+)', line)

            if match_rclone_errors:
                rclone_errors = match_rclone_errors[-1]

            if logging.DEBUG == logging.root.level:
                sys.stdout.write(line)
                sys.stdout.flush()

        popen.wait()

        end_time = time.time()

        self.metrics['rclone_start_time'].labels(source=bucket, destination=destination_bucket).set(start_time)
        self.metrics['rclone_end_time'].labels(source=bucket, destination=destination_bucket).set(end_time)
        self.metrics['rclone_rc'].labels(source=bucket, destination=destination_bucket).set(popen.returncode)
        self.metrics['rclone_errors'].labels(source=bucket, destination=destination_bucket).set(rclone_errors)

        return popen.returncode
