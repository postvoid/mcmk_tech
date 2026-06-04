FROM python:3.12-slim

WORKDIR /app

COPY ./bot/requirements.txt /app/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY ./bot /app/bot

ENV PYTHONPATH=/app

CMD ["python", "bot/bot.py"]