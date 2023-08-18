FROM python:3.11
LABEL authors="ATurret"
COPY ./ /app
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
RUN apt-get update && \
    apt-get install --no-install-recommends -y && \
    apt-get install -y ffmpeg
RUN curl -sSL https://install.python-poetry.org | python &&  \
    poetry install --no-dev
CMD poetry run gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:app