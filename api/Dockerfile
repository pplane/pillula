FROM python:3.7.0-slim-stretch

ADD ./src /src
WORKDIR /src

RUN pip install -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--reload", "api:app"]