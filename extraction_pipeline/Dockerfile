# The dockerfile to package the ASGI service

# Necessary environment variables
# MYSQL_USER=${USER}
# MYSQL_PASSWORD Set whatever you want
# MYSQL_DATABASE = "db"
# MYSQL_HOST="database" # for Docker container orchestration

# To build
# docker build --tag=ent-extraction ./
# To run
# docker run --name extraction_container --network bilby-assignment_bilby -e MYSQL_USER=$USER \
#  -e MYSQL_PASSWORD=$MYSQL_PASSWORD -e MYSQL_DATABASE=$MYSQL_DATABASE -e NER_HOST=$NER_HOST -e MYSQL_HOST=$MYSQL_HOST



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