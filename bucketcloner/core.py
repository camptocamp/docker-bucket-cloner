#!/usr/bin/env python3

import os
import argparse
import logging
from prometheus_client import Gauge
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from .api import ThreadedHTTPServer
from .backends import Backend

def _setup_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(log_level))
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

def _start_server(address, port):
    server = ThreadedHTTPServer(address, port)
    server.start()
    logging.info("HTTP server started on {}:{}".format(address, port))
    return server

def _list_buckets(backend):
    return backend.list_buckets()

def _run_main(backend, scheduler):
    logging.info("Starting main job")
    buckets = backend.list_buckets()

    running_job_ids = ""

    for job in scheduler.get_jobs():
        if not job.id in buckets:
            job.remove()
        else:
            running_job_ids.append(job.id)

    for bucket in buckets:
        if not bucket in running_job_ids:
            logging.info("Creating job for bucket `{}`".format(bucket))
            scheduler.add_job(_run_bc, id=bucket, misfire_grace_time=86400, args=[backend, bucket])

def _run_bc(backend, bucket):
    logging.info("Starting job for `{}`".format(bucket))
    rc = backend.run_rclone(bucket)
    if rc != 0:
        logging.error("Job for `{}` didn't run successfully: {}".format(bucket))
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

    backend = Backend(args.destination_pattern, args.whitelist, env_prefix="RCLONE_CONFIG_SRC")

    main_scheduler = BlockingScheduler()
    bc_scheduler = BackgroundScheduler()

    main_scheduler.add_job(_run_main, trigger=CronTrigger.from_crontab(args.schedule), coalesce=True, args=[backend, bc_scheduler])

    server = _start_server(args.address, args.port)

    bc_scheduler.start()

    try:
        main_scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

    server.stop()

if __name__ == '__main__':
    main()
