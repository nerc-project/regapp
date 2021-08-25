FROM docker.io/postgres:10
COPY init.sh /docker-entrypoint-initdb.d/
RUN chmod a+x /docker-entrypoint-initdb.d/init.sh