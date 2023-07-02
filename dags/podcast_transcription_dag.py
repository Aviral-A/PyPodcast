from datetime import timedelta
from airflow import DAG
from airflow.utils.dates import days_ago
from operators.search_and_create_sensors import create_podcast_sensor_and_task

dag = DAG(
    "podcast_transcription",
    default_args={
        "owner": "airflow",
        "retries": 0,
        "retry_delay": timedelta(minutes=5),
    },
    description="Transcribe and store latest podcast episodes",
    schedule_interval=None,  # Set to None to prevent scheduled runs, only manual triggers
    start_date=days_ago(1),
    catchup=False,
)

podcast_name = "{{ dag_run.conf['podcast_name'] }}"
sensor, transcribe_task = create_podcast_sensor_and_task(podcast_name, dag)