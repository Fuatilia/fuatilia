FROM python:3.12-slim-bookworm
WORKDIR /fuatilia
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
EXPOSE 8000
ENTRYPOINT ["python" , "app/main.py"]
