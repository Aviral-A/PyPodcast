import feedparser
from airflow.exceptions import AirflowSkipException
from airflow.sensors.base import BaseSensorOperator

class RSSFeedSensor(BaseSensorOperator):
    def __init__(self, rss_url, last_episode_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rss_url = rss_url
        self.last_episode_url = last_episode_url

    def poke(self, context):
        feed = feedparser.parse(self.rss_url)
        latest_episode_url = feed.entries[0].enclosures[0].url

        if latest_episode_url != self.last_episode_url:
            context["task_instance"].xcom_push("new_episode_url", latest_episode_url)
            return True
        else:
            raise AirflowSkipException("No new episode found")