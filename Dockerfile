FROM python:3.11.0
WORKDIR /
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
