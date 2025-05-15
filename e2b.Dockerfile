# You can use most Debian-based base images
FROM ubuntu:22.04

# Install dependencies and customize sandbox
FROM e2bdev/code-interpreter:latest
#RUN pip install cowsay
# RUN Rscript -e "install.packages('ggplot2', repos='https://cloud.r-project.org')"
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      r-base \
      r-base-dev \
      libcurl4-openssl-dev \
      libssl-dev \
      libxml2-dev \
 && rm -rf /var/lib/apt/lists/* \
 && Rscript -e "install.packages('ggplot2', repos='https://cloud.r-project.org')" \