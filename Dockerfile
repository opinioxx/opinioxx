FROM python:3.9

RUN mkdir /opinioxx && \
    mkdir /data && \
    mkdir /etc/opinioxx && \
    useradd -s /bin/bash -d /opinioxx -u 12421 opinioxxuser

COPY src /opinioxx/src
COPY deployment/docker/run.sh /opinioxx/run.sh
COPY deployment/docker/settings_demo.py /opinioxx/src/opinioxx/settings.py

WORKDIR /opinioxx

RUN pip install -r src/requirements.txt && \
    chmod 700 /opinioxx/run.sh &&  \
    chown -R opinioxxuser:opinioxxuser /opinioxx /data

USER opinioxxuser
EXPOSE 8000
ENTRYPOINT ["/opinioxx/run.sh"]