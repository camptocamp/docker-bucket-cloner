FROM debian:stretch

RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install --no-install-recommends -y curl unzip python-pip python-setuptools && \
	rm -rf /var/lib/apt/lists/*

RUN pip install wheel && pip install python-swiftclient python-keystoneclient s3cmd

RUN curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip
RUN unzip rclone-current-linux-amd64.zip
RUN cp rclone-*-linux-amd64/rclone /bin/rclone

ADD ./main.sh /
RUN chmod +x /main.sh

ENTRYPOINT ["/main.sh"]
CMD [""]
