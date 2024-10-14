Fuatilia

```
repo structure
|--app
    |--apps
        |---(Each app with their models, urls, ....)
    |--settings.py
    |--utils (generic functions/classes)
    |-- __init_.py
    |--asgi.py
    |--wsgi.py
    |--manage.py
|--.dockerignore
|--.gitignore
|--Dockerfile
|--requirements.txt
```

***To run locally*** <br>
`python -m venv venv` <br>
`pip install -r requirements.txt` <br>
`python app/main.py` <br>

***To run on docker*** <br>
`docker build -t <_name_> .` <br>
`docker run -it --net=host <_name_>` <br>

***To run on docker (With OpenTelemetry)*** <br>
`docker compose up --build .` <br>

***To run tests (Locally)***<br>
`pytest --log-disable={{your current logger}}` <br>


*** To view celery logs ***
`cd app`
`celery -A settings worker --pool=solo -l info`<br>

Any serializer that are named xyz...Body do not have any functions tied to them e.g validate or update , they re mostly for the input schema
Those that end in xyz...Serializer implement the said functions

FOr any serializers that implements any functions , we default to the"xyz...Serializer" naming to avid duplication . And thus the same serilizer will function as the request body in the schema unless there is need to have a schema body that has different params than what the serializer needs.
