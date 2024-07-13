FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./TodoApp /app/TodoApp

CMD ["sh", "-c", "uvicorn TodoApp.main:app --port=8000 --host=0.0.0.0"]

EXPOSE 8000
