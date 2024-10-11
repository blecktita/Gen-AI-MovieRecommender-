## Overview

This project creates a Chatbot with the following components:

- Docker compose stack for local "deployment"
- An HTTP API for the chatbot agent
- A UI based on streamlit to interact with the chatbot


## Project Setup

### Project Requirements

- Python >=3.10
- Poetry
- Docker and Docker Compose

### Environment variables

Set the following environment variables in your `.env`

```dotenv
OPENAI_BASE_URL= < >
OPENAI_API_KEY=<your-bricks-llm-key>
TMDB_API_KEY=<your-tmdb-jwt>
```

### Python dependencies

Use poetry to install the project dependencies with:

```console
poetry install
```

### Data Setup

To set up the netflix datasource, download the [titles.csv](https://www.kaggle.com/datasets/victorsoeiro/netflix-tv-shows-and-movies) from the Kaggle dataset and place it on `data/titles.csv`.

We need to pre-process this data. To do it, run the following script:

```console
poetry run netflix-data
```

### Run the project

Run the following command to launch the stack

```console
docker compose up --build
```

Access the web UI on <http://localhost:8501/>
