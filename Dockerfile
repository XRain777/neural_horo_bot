# syntax=docker/dockerfile:1

FROM python:3.10.5-slim-buster as bot_base

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

FROM bot_base as bot_vk
CMD [ "python", "main.py" ]

FROM bot_base as bot_tg
CMD [ "python", "main_tg.py" ]
