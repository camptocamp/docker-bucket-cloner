FROM python:3

RUN curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip
RUN unzip rclone-current-linux-amd64.zip
RUN cp rclone-*-linux-amd64/rclone /bin/rclone

WORKDIR /app

COPY . .

RUN make deps && make install

USER 1000

ENTRYPOINT ["bkc"]
CMD [""]
