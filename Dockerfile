FROM python:3.7
LABEL maintainer=d.schuldt@eos-ts.com

COPY app /app
RUN pip install bottle pymongo gunicorn gevent gevent-websocket 

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:80", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "--chdir", "/app", "app:app"]
