# The dockerfile to package the ASGI service
# docker build --tag=ner-asgi ./
# docker run --publish 8081:8081 ner-asgi

ARG DISTRIBUTION=ghcr.io/astral-sh/uv:debian-slim
FROM $DISTRIBUTION
LABEL maintainer="Barman Roy, Swagato <swagatopablo@aol.com>"
WORKDIR /app
# Copy the necessary scripts and files
COPY *.sh ./
COPY src/*.* src/
COPY pyproject.toml ./

RUN chmod +x *.sh
# Fire up the service at container boot time.
CMD ["./run_asgi.sh"]