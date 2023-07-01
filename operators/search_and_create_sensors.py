from src.lookup_podcast import format_podcast_name
from src.lookup_podcast import fetch_rss_feed_url
from src.lookup_podcast import get_first_valid_enclosure_url
from .rss_feed_sensor import RSSFeedSensor
from airflow.operators.python import PythonOperator
from src.transcribe_and_store_audio import transcribe_and_store_audio

def _get_new_episode_url_from_sensor(**context):
    return context["task_instance"].xcom_pull(task_ids="rss_feed_sensor", key="new_episode_url")

def create_podcast_sensor_and_task(podcast_name, dag):
    rss_feed_url = fetch_rss_feed_url(podcast_name)
    last_episode_url = get_first_valid_enclosure_url(rss_feed_url)

    sensor = RSSFeedSensor(
        task_id=f"rss_feed_sensor_{rss_feed_url}",
        rss_url=rss_feed_url,
        last_episode_url=last_episode_url,
        timeout=30,
        poke_interval=60,
        mode="poke",
        dag=dag,
    )

    transcribe_task = PythonOperator(
        task_id=f"transcribe_podcast_{rss_feed_url}",
        python_callable=transcribe_and_store_audio(rss_feed_url),
        op_args=[_get_new_episode_url_from_sensor],
        provide_context=True,
        dag=dag,
    )

    sensor >> transcribe_task

    return sensor, transcribe_task

def create_episode_transcription_task(episode_url: str, dag):
    task = PythonOperator(
        task_id=f"transcribe_episode_{episode_url}",
        python_callable=transcribe_and_store_audio(episode_url),
        op_args=[episode_url],
        dag=dag,
    )

    return task