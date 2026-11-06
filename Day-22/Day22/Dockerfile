FROM apache/airflow:2.9.3-python3.11

COPY requirements.txt /requirements.txt

# The constraints file keeps Airflow's own package versions pinned, so adding
# Great Expectations and the Snowflake connector can't break Airflow.
RUN pip install --no-cache-dir -r /requirements.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.11.txt"
