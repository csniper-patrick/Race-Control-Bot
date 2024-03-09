FROM docker.io/library/python:3.12-alpine

WORKDIR /opt/
COPY ./requirements.txt ./race-control.py ./messageManager.py /opt/
RUN python -m pip install -r requirements.txt
CMD [ "python", "/opt/race-control.py" ]