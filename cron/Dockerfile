FROM postgres:11-alpine

MAINTAINER Paul Stevenson "pstevenson6@gmail.com"

COPY crontab /etc/crontabs/crontab
COPY .pgpass /home/.pgpass

RUN chown root:root /home/.pgpass && \
  chmod 0600 /home/.pgpass && \
  export PGPASSFILE='/home/.pgpass' && \
  crontab /etc/crontabs/crontab

CMD ["crond", "-f"]
