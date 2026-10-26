FROM apache/airflow:2.10.5-python3.11

COPY requirements-airflow.txt /tmp/requirements-airflow.txt
RUN pip install --no-cache-dir -r /tmp/requirements-airflow.txt

# Project code and DAGs are mounted by docker-compose, so no COPY needed here
ENV PYTHONPATH=/opt/airflow/etl_project
