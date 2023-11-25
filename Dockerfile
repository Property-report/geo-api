FROM python:3.9.14

COPY / /opt/

RUN pip3 install -q -r /opt/requirements.txt 
EXPOSE 8000

WORKDIR /opt

CMD ["/usr/local/bin/gunicorn", "-k", "eventlet", "--workers", "4", "--pythonpath", "/opt", "--access-logfile", "-", "manage:manager.app", "--reload", "-b", "0.0.0.0:8000"]
