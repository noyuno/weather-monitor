
FROM python:3-alpine
ENV PYTHONPATH=/usr/lib/python3.8/site-packages
COPY . /opt/weather-monitor
WORKDIR /opt/weather-monitor
RUN echo $'@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories && \
    apk --update add build-base python-dev py-pip py3-pillow font-noto-cjk font-noto-emoji@testing && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/apk/* && \
    pip3 install -r requirements-dev.txt
CMD [ "python3", "run.py" ]
