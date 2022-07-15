# docker-bucket-cloner

A tool to synchronize buckets between cloud prodivers regions or between cloud providers and expose prometheus metrics.


## Usage

To synchronize a bucket you just need to launch the docker image with the following environment variables :

* BKC_DAEMON_SCHEDULE : Cron style sheduling time to launch the sync tool (default: '0 1 * * *')
* DESTINATION_PATTERN (mandatory): Pattern for the destination (e.g : '[bucket]', will create a folder for each source bucket at the root of the dest bucket)
* WHITELIST : The tool lists all available bucket and filter them with a regex, for example '.\*production.\*' (default: none)
* RCLONE_CONFIG_* : A list of envars with the source and destination buckets configurations, see this [doc](https://rclone.org/docs/#environment-variables).

A basic example would look like :
````
      RCLONE_CONFIG_DST_ACCESS_KEY_ID: EXOXXX
      RCLONE_CONFIG_DST_ENDPOINT: https://sos-ch-gva-2.exo.io
      RCLONE_CONFIG_DST_SECRET_ACCESS_KEY: DESTINATIONSECRETACCESSKEY
      RCLONE_CONFIG_DST_TYPE: s3

      RCLONE_CONFIG_SRC_ACCESS_KEY_ID: SCWXXX
      RCLONE_CONFIG_SRC_REGION: fr-par
      RCLONE_CONFIG_SRC_SECRET_ACCESS_KEY: SOURCESECRETACCESSKEY
      RCLONE_CONFIG_SRC_TYPE: s3
      RCLONE_CONFIG_SRC_PROVIDER: Scaleway
````

Other optional envars :

* BKC_DAEMON_TIMEZONE : Set the timezone for the scheduler (default: 'UTC')
* BKC_DAEMON_LOG_LEVEL : By default only schedulers infos are printed, set to DEBUG to have all schedulers operations and rclone stats and transfers (default: 'INFO')
* BKC_DAEMON_ADDRESS : Adress where the daemon expose the prometheus metrics (default: '0.0.0.0')
* BKC_DAEMON_PORT : Port where the daemon expose the prometheus metrics (default: '8581')

## Scheduling

The tool uses two schedulers, one that launches when triggered by the cron time, lists all the buckets to synchronize and add a job for each bucket in a second scheduler that runs in the background.

The second scheduler then add the sync job to its queue if not already in it, launches it and remove it. There is a parralelization of 10 jobs at a time, and a job is expired after 24h in the queue.
