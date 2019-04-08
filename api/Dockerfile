FROM python:alpine

MAINTAINER Paul Stevenson "pstevenson6@gmail.com"

COPY ./app /app

WORKDIR /app

# add and install requirements
RUN apk update && \
 apk add postgresql-libs && \
 apk add --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

ENTRYPOINT ["python"]

CMD ["app.py"]
