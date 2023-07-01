from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import feedparser
import undetected_chromedriver as uc
import requests
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import re
from typing import List
from xml.etree import ElementTree

def format_podcast_name(podcast_name):
    formatted_name = podcast_name.lower().replace(" ", "-").replace(",", "").replace(".", "").replace(":", "")
    return formatted_name


def fetch_rss_feed_url(podcast_name):
    formatted_name = format_podcast_name(podcast_name)
    url = f"https://player.fm/series/{formatted_name}"
    options = Options()
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--enable-javascript')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-infobars")
    uc.TARGET_VERSION = 114
    driver = uc.Chrome(options=options)
    driver.get(url)

    try:
        rss_feed_element = driver.find_element(By.XPATH, "//a[contains(text(), 'Feed')]")
        rss_feed_url = rss_feed_element.get_attribute("href")

    except:
        raise Exception(f"Could not find RSS feed URL for podcast '{podcast_name}'")
    

    driver.quit()

    return rss_feed_url

def get_first_valid_enclosure_url(rss_feed_url):
    feed = feedparser.parse(rss_feed_url)
    for entry in feed.entries:
        for enclosure in entry.enclosures:
            if enclosure.type == "audio/mpeg":
                return enclosure.url
    return None


def tokenize_and_remove_stop_words(title: str, nlp) -> List[str]:
    doc = nlp(title.lower())
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return tokens

def spacy_similarity(title1: str, title2: str, nlp) -> float:
    doc1 = nlp(" ".join(title1))
    doc2 = nlp(" ".join(title2))
    return doc1.similarity(doc2)

def clean_title(title: str) -> str:
    return title.strip()
