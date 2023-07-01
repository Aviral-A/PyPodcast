from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from operators.search_and_create_sensors import create_podcast_sensor_and_task

def run_podcast_transcription_dag(**context):
    podcast_name = context["dag_run"].conf["podcast_name"]
    sensor, task = create_podcast_sensor_and_task(podcast_name, context["dag"])
    context["dag"].add_task(sensor)
    context["dag"].add_task(task)

dag = DAG(
    "podcast_transcription",
    default_args={
        "owner": "airflow",
        "retries": 0,
        "retry_delay": timedelta(minutes=5),
    },
    description="Transcribe and store podcast episodes",
    schedule_interval=None,  # Set to None to prevent scheduled runs, only manual triggers
    start_date=days_ago(1),
    catchup=False,
)

run_podcast_transcription_task = PythonOperator(
    task_id='run_podcast_transcription',
    python_callable=run_podcast_transcription_dag,
    provide_context=True,
    dag=dag,
)