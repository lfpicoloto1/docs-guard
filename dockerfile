FROM python:3.12

WORKDIR /app

COPY requirements.txt requirements.txt
COPY main.py main.py
COPY test_main.py test_main.py

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
