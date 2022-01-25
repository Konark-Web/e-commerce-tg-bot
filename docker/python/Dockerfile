FROM python:3.9-slim

COPY /app /opt/app

WORKDIR /opt/app

RUN pip3 install -r requirements.txt

COPY ./docker/python/entrypoint.sh /opt/app/entrypoint.sh

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
