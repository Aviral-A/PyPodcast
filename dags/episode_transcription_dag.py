from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from operators.search_and_create_sensors import create_episode_transcription_task

def run_episode_transcription_dag(**context):
    episode_url = context["dag_run"].conf["episode_url"]
    task = create_episode_transcription_task(episode_url, context["dag"])
    context["dag"].add_task(task)

dag = DAG(
    "episode_transcription",
    default_args={
        "owner": "airflow",
        "retries": 0,
        "retry_delay": timedelta(minutes=5),
    },
    description="Transcribe and store specific podcast episode",
    schedule_interval=None,  # Set to None to prevent scheduled runs, only manual triggers
    start_date=days_ago(1),
    catchup=False,
)

run_episode_transcription_task = PythonOperator(
    task_id='run_episode_transcription',
    python_callable=run_episode_transcription_dag,
    provide_context=True,
    dag=dag,
)