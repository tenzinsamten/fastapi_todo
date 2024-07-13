FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./TodoApp /app/TodoApp

EXPOSE 10000

CMD ["sh", "-c", "uvicorn TodoApp.main:app --port=10000 --host=0.0.0.0"]

