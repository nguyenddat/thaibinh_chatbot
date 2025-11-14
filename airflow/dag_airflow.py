import os
import json
import sys

from airflow.decorators import dag, task
from datetime import timedelta
from airflow.utils.dates import days_ago
from airflow.datasets import Dataset

def task_load_data(**kwargs):
    for db in get_db():
        data = load_raw_data(db)
        kwargs['ti'].xcom_push(key='raw_data', value=data)