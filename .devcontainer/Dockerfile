FROM python:3-alpine

RUN apk --update add tzdata \
    && cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && apk del tzdata \
    && rm -rf /var/cache/apk/* \
    && echo 'Asia/Tokyo' > /etc/timezone

WORKDIR /usr/src/app

COPY .. .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]
