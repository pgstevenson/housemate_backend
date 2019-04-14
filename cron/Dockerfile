FROM postgres:11-alpine

MAINTAINER Paul Stevenson "pstevenson6@gmail.com"

ENV TZ=Australia/Perth

RUN mkdir /home/postgres

COPY ./crontab /etc/crontabs/crontab
COPY ./.pgpass /home/postgres/.pgpass

RUN chown -R postgres:postgres /home/postgres/ && \
  chmod 0600 /home/postgres/.pgpass && \
  crontab /etc/crontabs/crontab

ENV PGPASSFILE='/home/postgres/.pgpass'

CMD ["crond", "-f"]
