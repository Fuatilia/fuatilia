FROM python:3.12-slim-bookworm

WORKDIR /fuatilia

COPY . .

RUN mkdir logs && \
    pip install --no-cache-dir --upgrade -r requirements.txt && \
    chmod +x /fuatilia/scripts/fuatilia.sh

EXPOSE 8000

ENTRYPOINT ["/fuatilia/scripts/fuatilia.sh"]
