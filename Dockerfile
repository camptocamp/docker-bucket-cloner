FROM debian:stretch

RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install --no-install-recommends -y curl unzip python-pip python-setuptools && \
	rm -rf /var/lib/apt/lists/*

RUN pip install wheel && pip install python-swiftclient python-keystoneclient s3cmd

RUN curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip
RUN unzip rclone-current-linux-amd64.zip
RUN cp rclone-*-linux-amd64/rclone /bin/rclone

WORKDIR /app

ADD ./main.sh .
RUN chmod +x ./main.sh

RUN chown 1000:1000 -R /app

RUN chgrp -R 0 /app && \
    chmod -R g=u /app
RUN chmod g=u /etc/passwd

USER 1000

ENTRYPOINT ["./main.sh"]
CMD [""]
