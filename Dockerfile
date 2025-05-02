# use whatever base you like
FROM python:3.12

# pick a working dir inside the container
WORKDIR /app

# 1) copy only the server requirements, so Docker can cache this layer
COPY server/requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# 2) now copy the rest of your server code
COPY server/ .

# 3) run uvicorn from inside /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]