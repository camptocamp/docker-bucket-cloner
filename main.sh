#!/bin/bash

usage() { echo "Usage: $0 [-d <destination-pattern>] [-w <whitelist>]" 1>&2; exit 1; }

while getopts ":d:w:" o; do
  case "${o}" in
    d)
      DESTINATION_PATTERN=${OPTARG}
      ;;
    w)
      WHITELIST=${OPTARG}
      ;;
    *)
      usage
      ;;
  esac
done
shift $((OPTIND-1))

if [ -z "${DESTINATION_PATTERN}" ]; then
  usage
fi

if [[ "$RCLONE_CONFIG_SRC_TYPE" == "s3" ]]; then

  # Validate variables
  if [ -z "$RCLONE_CONFIG_SRC_ACCESS_KEY_ID" ]; then
    echo "[-] You must set the variable RCLONE_CONFIG_SRC_ACCESS_KEY_ID must be set."
    exit 1
  elif [ -z "$RCLONE_CONFIG_SRC_SECRET_ACCESS_KEY" ]; then
    echo "[-] You must set the variable RCLONE_CONFIG_SRC_SECRET_ACCESS_KEY must be set."
    exit 1
  elif [ -z "$RCLONE_CONFIG_SRC_ENDPOINT" ]; then
    echo "[-] You must set the variable RCLONE_CONFIG_SRC_ENDPOINT must be set."
    exit 1
  fi

  raw_buckets=$(s3cmd --access_key="$RCLONE_CONFIG_SRC_ACCESS_KEY_ID" --secret_key="$RCLONE_CONFIG_SRC_SECRET_ACCESS_KEY" --host="$RCLONE_CONFIG_SRC_ENDPOINT" ls | cut -d / -f 3)

elif [[ "$RCLONE_CONFIG_SRC_TYPE" == "swift" ]]; then

  export OS_AUTH_URL=$RCLONE_CONFIG_SRC_AUTH
  export OS_USER_DOMAIN_NAME=$RCLONE_CONFIG_SRC_DOMAIN
  export OS_PASSWORD=$RCLONE_CONFIG_SRC_KEY
  export OS_REGION=$RCLONE_CONFIG_SRC_REGION
  export OS_TENANT=$RCLONE_CONFIG_SRC_TENANT
  export OS_TENANT_ID=$RCLONE_CONFIG_SRC_TENANT_ID
  export OS_USERNAME=$RCLONE_CONFIG_SRC_USER

  raw_buckets=$(swift list)

else
  echo "[-] Type not recognized, please use s3 or swift."
  exit 1
fi

if [ $? -ne 0 ]; then
  echo "[-] Failed to list buckets on source."
  exit 1
fi

for bucket in $raw_buckets; do
  if [[ "$bucket" =~ $WHITELIST ]]; then

    # Replace [bucket] if needed
    DESTINATION=${DESTINATION_PATTERN//\[bucket\]/$bucket}

    rclone -vv sync --s3-acl private src:"$bucket" dst:"$DESTINATION"
    if [ $? -eq 0 ]; then
      echo "[+] Bucket $bucket successfully synchronized."
    else
      echo "[-] Failed to backup $bucket."
    fi
  fi
done
