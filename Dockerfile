FROM python:3.10-slim@sha256:b22d43a1278b3d417219cc2cdc375866d23ebcfb9d852b13b974d421158f6c08

ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PIP_NO_CACHE_DIR 1

# Add non-root user
RUN groupadd detective && \
    useradd -r --no-create-home detective -g detective

# Handle folder permissions
RUN mkdir /app && chown detective:detective /app
WORKDIR /app

# Install external dependencies separately (can be cached)
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=detective:detective . .

RUN pip install -e . && \
    rm requirements.txt

# Run application as non-root user
USER detective

# Required for docker-slim http probing
EXPOSE 3004

CMD uvicorn src.feedme_service.service.server:app --host 0.0.0.0 --port 3004