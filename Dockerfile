FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 80
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]