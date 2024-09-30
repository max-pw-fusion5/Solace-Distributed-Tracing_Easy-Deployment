FROM python:3-alpine

COPY solace-dt-init.py /tmp/solace-init.py
COPY queues.json /tmp/queues.json
COPY dt-setup.json /tmp/dt-setup.json


USER root
RUN python -m pip install --upgrade pip
RUN python -m pip install requests
USER 1001

ENTRYPOINT [ "python", "/tmp/solace-init.py" ]