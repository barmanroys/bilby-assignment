# The dockerfile to package the extraction job
# Necessary environment variables
# MYSQL_USER
# MYSQL_PASSWORD
# MYSQL_DATABASE
# MYSQL_HOST="database" # for docker compose orchestration
# NER_HOST = ner # For docker compose orchestration
# Also, include the container in the local bridge network called `bilby-assignment_bilby` for service discovery.


ARG DISTRIBUTION=ghcr.io/astral-sh/uv:debian-slim
FROM $DISTRIBUTION
LABEL maintainer="Barman Roy, Swagato <swagatopablo@aol.com>"

WORKDIR /app

# Copy the necessary scripts and files
COPY *.sh ./
COPY src/*.* src/
COPY data/*.parquet data/
COPY pyproject.toml ./

RUN chmod +x *.sh
# Fire up the job at container boot time.
CMD ["./run_job.sh"]