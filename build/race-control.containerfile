FROM docker.io/library/python:3.12-alpine

WORKDIR /opt/
COPY ./requirements.txt ./race-control.py ./emoji-symbol-example.json /opt/
COPY ./messageManager/ /opt/messageManager/
RUN python -m pip install -r requirements.txt
CMD [ "python", "/opt/race-control.py" ]