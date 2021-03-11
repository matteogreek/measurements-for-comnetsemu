FROM python:3.6-alpine3.9

COPY ./twampy.py /home/twampy.py

CMD python /home/twampy.py