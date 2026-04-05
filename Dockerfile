FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install aiogram
CMD ["python", "app.py"]

