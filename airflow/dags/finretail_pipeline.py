from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def generate_data():
    from src.generator.source_generator import main
    main()


def upload_to_minio():
    from src.generator.land_to_minio import main
    main()


def register_files():
    from src.ingestion.register_landed_files import register_files
    register_files()


def load_raw():
    from src.ingestion.load_raw_from_minio import main
    main()


def bronze():
    from src.transform.bronze import main
    main()


def silver():
    from src.transform.silver import main
    main()


def gold():
    from src.transform.gold import main
    main()


with DAG(
    dag_id="finretail_lakehouse_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["finretail", "lakehouse", "portfolio"],
) as dag:

    t1 = PythonOperator(
        task_id="generate_data",
        python_callable=generate_data,
    )

    t2 = PythonOperator(
        task_id="upload_to_minio",
        python_callable=upload_to_minio,
    )

    t3 = PythonOperator(
        task_id="register_landed_files",
        python_callable=register_files,
    )

    t4 = PythonOperator(
        task_id="load_raw_from_minio",
        python_callable=load_raw,
    )

    t5 = PythonOperator(
        task_id="bronze_transform",
        python_callable=bronze,
    )

    t6 = PythonOperator(
        task_id="silver_transform",
        python_callable=silver,
    )

    t7 = PythonOperator(
        task_id="gold_transform",
        python_callable=gold,
    )

    t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7