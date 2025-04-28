# Commands to run airflow standalone
# docker build . --tag airflow-local
# docker run --publish 8080:8080 -v /c/local/clone/path/airflow-examples/dags:/opt/airflow/dags  -d airflow-local

FROM apache/airflow:2.9.0-python3.9
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
USER root
RUN apt-get update && apt-get install -y \
    wget
COPY start.sh /start.sh
RUN chmod +x /start.sh
USER airflow
ENTRYPOINT ["/bin/bash","/start.sh"]