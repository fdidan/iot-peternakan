FROM mysql:8.0

ENV MYSQL_DATABASE=iot_peternakan
ENV MYSQL_ROOT_PASSWORD=root
ENV MYSQL_USER=root

COPY init.sql /docker-entrypoint-initdb.d/
