FROM docker:stable-dind

RUN apk add python3
RUN apk add build-base
RUN apk add bash bash-completion
RUN apk add iproute2 busybox-extras iperf3

RUN apk add stress-ng curl tcpdump netcat-openbsd
RUN apk update && apk upgrade

COPY ./twampy.py /home/twampy.py

ENV HOME /root
WORKDIR /root

# Define default command.
CMD ["bash"]