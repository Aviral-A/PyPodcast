# PyPodcast

This project is a service that takes in user inputs to search for podcast episode titles based on keyword search with three types of matching - exact, fuzzy, and simliarity. This service also takes in a podcast name inputted by the user, scrapes the respective RSS feed, and adds the podcast to a Transcription DAG that gets triggered on each episode, determined by the delta in the time between episodes from the XML file for the RSS feed. Embeddings of speakers from podcasts are stored in a PostgresQL Database. Work in progress.
