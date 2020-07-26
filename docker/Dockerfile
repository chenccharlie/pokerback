# pull official base image
FROM python:3.6.5

RUN apt-get -y update && \
    apt-get -y install \
        netcat

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
# RUN apk update \
#     && apk add postgresql-dev gcc python3-dev musl-dev

# copy project
COPY . /app

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

# run entrypoint.sh
ENTRYPOINT ["/app/docker/entrypoint.sh"]