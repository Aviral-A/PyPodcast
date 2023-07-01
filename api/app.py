# Import additional required modules
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .transcription_api import trigger_podcast_transcription_dag, search_podcast_episodes, trigger_episode_transcription_dag

app = FastAPI()

class PodcastName(BaseModel):
    podcast_name: str

class EpisodeTitle(BaseModel):
    episode_title: str

@app.post("/transcribe_podcast", status_code=201)
async def transcribe_podcast(podcast_name: PodcastName):
    try:
        if not podcast_name.podcast_name:
            raise HTTPException(status_code=400, detail="Podcast name cannot be empty")

        trigger_podcast_transcription_dag(podcast_name.podcast_name)

        return {
            "message": "Podcast transcription DAG triggered successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/search_episodes", status_code=200)
async def search_episodes(podcast_name: str, episode_title: str):
    try:
        if not podcast_name:
            raise HTTPException(status_code=400, detail="Podcast name cannot be empty")

        if not episode_title:
            raise HTTPException(status_code=400, detail="Episode title cannot be empty")

        episodes = search_podcast_episodes(podcast_name, episode_title)

        return {
            "episodes": episodes,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe_episode", status_code=201)
async def transcribe_episode(episode_url: str):
    try:
        if not episode_url:
            raise HTTPException(status_code=400, detail="Episode URL cannot be empty")

        trigger_episode_transcription_dag(episode_url)

        return {
            "message": "Episode transcription DAG triggered successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))