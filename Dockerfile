# use whatever base you like
FROM python:3.12

# pick a working dir inside the container
WORKDIR /app

# 1) copy only the server requirements, so Docker can cache this layer
COPY server/requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

 # ─── Install R and system dependencies ─────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
r-base \
r-base-dev \
libcurl4-openssl-dev \
libssl-dev \
libxml2-dev \
&& rm -rf /var/lib/apt/lists/*

# ─── Install R graphing packages ───────────────────────────────────────────────
RUN Rscript -e "install.packages(c('ggplot2', 'lattice', 'plotly'), repos='https://cloud.r-project.org/')"

# 2) now copy the rest of your server code
COPY server/ .

# 3) run uvicorn from inside /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]