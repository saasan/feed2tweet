FROM python:3

RUN ln -snf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
        && echo 'Asia/Tokyo' > /etc/timezone

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]
