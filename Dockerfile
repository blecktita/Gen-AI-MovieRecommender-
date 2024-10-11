FROM python:3.10-slim AS base

ENV \
    PROJECT_HOME="/opt/project" \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=Europe/Madrid \
    DEBIAN_FRONTEND=noninteractive \
    # Python Settings
    # Disables writing .pyc files. Set it back to 0 if using multiprocessing as it will save time spawning new processes
    PYTHONDONTWRITEBYTECODE=1 \
    # Stops Python from buffering stdout and stderr
    PYTHONUNBUFFERED=1 \
    # Turns off pip self version checks when calling pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # Poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.8.2 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # never create virtual environment automatically, only use env prepared by us
    POETRY_VIRTUALENVS_CREATE=false \
    # this is where our requirements + virtual environment will live
    VIRTUAL_ENV="/venv" \
    # Guarantees the virtualenv can be moved between build stages
    VIRTUALENV_COPIES=1

WORKDIR ${PROJECT_HOME}

# hadolint ignore=DL3059
RUN addgroup clarity \
    && adduser --ingroup clarity clarity \
    && chown -R clarity:clarity ${PROJECT_HOME}

# Prepend poetry and venv to path. Set PYTHONPATH
ENV \
    PATH="${POETRY_HOME}/bin:${VIRTUAL_ENV}/bin:${PATH}" \
    PYTHONPATH="${PROJECT_HOME}:${PYTHONPATH}"

# Prepare virtualenv
RUN python -m venv "${VIRTUAL_ENV}"

# Update and install common packages
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

###########################
###### DEPENDENCIES #######
###########################
FROM base AS dependencies

# This address https://github.com/hadolint/hadolint/wiki/DL4006
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# Install poetry - respects ${POETRY_VERSION} & ${POETRY_HOME}
# The --mount will mount the buildx cache directory to where
# Poetry and Pip store their cache so that they can re-use it
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python -

# Used to init dependencies
COPY poetry.lock pyproject.toml ./
# Install runtime deps to $VIRTUAL_ENV
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main --compile
##########################
######### CHAT UI ########
##########################
FROM base AS chat-ui

# Turn off Streamlit file watcher (autoreload)
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

COPY --from=dependencies $POETRY_HOME $POETRY_HOME
COPY --from=dependencies $VIRTUAL_ENV $VIRTUAL_ENV
COPY poetry.lock pyproject.toml ./

ARG DEPENDENCY_GROUP="ui"

RUN --mount=type=cache,target=/root/.cache \
    poetry install --only ${DEPENDENCY_GROUP} --no-root --compile

COPY chat_ui chat_ui

ENTRYPOINT ["streamlit", "run"]
CMD ["chat_ui/main.py"]

###########################
########### API ###########
###########################
FROM base AS api

ENV UVICORN_PORT=8080
ENV UVICORN_HOST=0.0.0.0

EXPOSE ${UVICORN_PORT}

USER clarity

# Copy in our built poetry + venv
COPY --from=dependencies $POETRY_HOME $POETRY_HOME
COPY --from=dependencies $VIRTUAL_ENV $VIRTUAL_ENV

COPY poetry.lock pyproject.toml ./
COPY app app

ENTRYPOINT ["uvicorn"]
CMD ["app.server:app"]
