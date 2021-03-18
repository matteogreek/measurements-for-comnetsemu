FROM docker:stable-dind

COPY ./twampy.py /home/twampy.py

RUN apk update && apk upgrade
RUN apk add python3

RUN apk add bash bash-completion
RUN apk add iproute2 busybox-extras iperf

RUN apk add stress-ng curl tcpdump netcat-openbsd

ENV HOME /root
WORKDIR /root

# Define default command.
CMD ["bash"]