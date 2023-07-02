FROM python:3.10.10

WORKDIR /app

RUN apt-get update && \
    apt-get install -y libsndfile1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 80

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "80"] 