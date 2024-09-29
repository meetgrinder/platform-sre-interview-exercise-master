# Provide Dockerfile here to build image for your app
FROM python:3.7
RUN apt update
RUN apt install -y vim
RUN apt install -y which
RUN apt install -y procps
RUN apt install -y findutils
WORKDIR /src
COPY src/ .
RUN python -m pip install -r requirements.txt
EXPOSE 8000
ENTRYPOINT ["python", "/src/currency_api/api.py"]


