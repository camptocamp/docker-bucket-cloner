#!/usr/bin/env python3

import os
import argparse
import logging
from prometheus_client import Gauge
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from .api import ThreadedHTTPServer
from .backends import Backend

def _setup_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(log_level))
    logging.basicConfig(level=numeric_level)

def _start_server(address, port):
    server = ThreadedHTTPServer(address, port)
    server.start()
    logging.info("HTTP server started on {}:{}".format(address, port))
    return server

def _list_buckets(backend):
    return backend.list_buckets()

def _run_bc(backend, bucket):
    logging.info("Starting job for `{}`".format(bucket))
    rc, output = backend.run_rclone(bucket)
    if rc != 0:
        logging.error("Job for `{}` didn't run successfully: {}".format(bucket, output))
    else:
        logging.info("Job for `{}` successfully executed".format(bucket))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", help="Cron-style scheduling.",
                        type=str, default=os.environ.get(
                            'BKC_DAEMON_SCHEDULE', '0 1 * * *'))
    parser.add_argument("--log-level", help="Logging level.",
                        type=str, default=os.environ.get(
                            'BKC_DAEMON_LOG_LEVEL', 'INFO'))
    parser.add_argument("--address", help="Address the daemon should bind on.",
                        type=str, default=os.environ.get(
                            'BKC_DAEMON_ADDRESS', '0.0.0.0'))
    parser.add_argument("--port", help="Port the daemon should listen on.",
                        type=int, default=os.environ.get(
                            'BKC_DAEMON_PORT', 8581))
    parser.add_argument("--destination-pattern",
                        help="Bucket destination pattern.",
                        type=str, default=os.environ.get(
                            'DESTINATION_PATTERN'))
    parser.add_argument("--whitelist", help="Whitelist of buckets to clone.",
                        type=str, default=os.environ.get(
                            'WHITELIST'))

    args, unknown = parser.parse_known_args()
    _setup_logging(args.log_level)
    scheduler = BlockingScheduler()
    backend = Backend(args.destination_pattern, args.whitelist, env_prefix="RCLONE_CONFIG_SRC")

    buckets = backend.list_buckets()
    for bucket in buckets:
        logging.info("Creating job for bucket `{}`".format(bucket))
        scheduler.add_job(_run_bc, CronTrigger.from_crontab(args.schedule), args=[backend, bucket])

    server = _start_server(args.address, args.port)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

    server.stop()

if __name__ == '__main__':
    main()
