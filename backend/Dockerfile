FROM python:3.11
WORKDIR /app
ENV PYTHONUNBUFFERED 1
COPY requirements.txt .
RUN pip install -r /app/requirements.txt --no-cache-dir
COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]