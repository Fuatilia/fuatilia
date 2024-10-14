FROM python:3.12-slim-bookworm
WORKDIR /fuatilia
COPY requirements.txt ./
RUN mkdir logs
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
RUN ["chmod", "+x" , "/fuatilia/scripts/fuatilia.sh"]
ENTRYPOINT ["/fuatilia/scripts/fuatilia.sh"]
