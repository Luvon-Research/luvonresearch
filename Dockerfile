FROM python:3.12

WORKDIR /server

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt  # Install dependencies

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
