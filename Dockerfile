FROM python:3.11.0
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt
COPY . /app
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]