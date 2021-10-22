FROM  docker.io/python:3.9.6
RUN pip install pip-tools
COPY requirements.in /tmp/requirements.in
RUN pip-compile -o /tmp/requirements.txt /tmp/requirements.in

FROM  docker.io/python:3.9.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code /code/log /static /scripts
WORKDIR /code

RUN apt-get update && apt-get install -y \
    vim

COPY manage.py /code/
COPY --from=0 /tmp/requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
# Patch around bug in runner for time being

COPY containers/regapp/entrypoint.sh /scripts/
RUN chmod 755 /scripts/*.sh
COPY . /code/regapp/
