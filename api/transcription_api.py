from operators.search_and_create_sensors import create_podcast_sensor_and_task as _create_podcast_sensor_and_task
from src.lookup_podcast import fetch_rss_feed_url
from src.searchEpisodes import search_episodes_by_title
from airflow import settings
from airflow.models import DagBag
import requests


def trigger_podcast_transcription_dag(podcast_name: str):
    airflow_api_url = "http://localhost:8080/api/experimental/dags/podcast_transcription/dag_runs"
    headers = {"Content-Type": "application/json"}
    data = {"conf": {"podcast_name": podcast_name}}

    response = requests.post(airflow_api_url, headers=headers, json=data)

    if not response.ok:
        raise Exception(f"Failed to trigger DAG: {response.text}")

    return response.json()

def create_podcast_sensor_and_task(podcast_name):
    dag_id = "podcast_transcription"
    dag_bag = DagBag(settings.DAGS_FOLDER)
    dag = dag_bag.get_dag(dag_id)

    if not dag:
        raise Exception(f"DAG with id '{dag_id}' not found")

    sensor, task = _create_podcast_sensor_and_task(podcast_name, dag)

    dag.add_task(sensor)
    dag.add_task(task)

    return sensor, task

def search_podcast_episodes(podcast_name: str, episode_title: str):
    rss_feed_url = fetch_rss_feed_url(podcast_name)
    return search_episodes_by_title(rss_feed_url, episode_title)

def trigger_episode_transcription_dag(episode_url: str):
    airflow_api_url = "http://localhost:8080/api/experimental/dags/episode_transcription/dag_runs"
    headers = {"Content-Type": "application/json"}
    data = {"conf": {"episode_url": episode_url}}

    response = requests.post(airflow_api_url, headers=headers, json=data)

    if not response.ok:
        raise Exception(f"Failed to trigger DAG: {response.text}")

    return response.json()