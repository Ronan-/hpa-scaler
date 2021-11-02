# syntax=docker/dockerfile:1
FROM python:3.10-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY hpa-scaler.py LICENSE README.md .

CMD [ "python", "./hpa-scaler.py" ]