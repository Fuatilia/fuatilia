**Fuatilia**

repo structure
|--app
    |--models
    |--routes
    |--services `(modularized functions specifically tied to model implemetation)`
    |--utils `(generic functions/classes)`
    |-- __init_.py
    |--db.py
    |--main.py
|--Dockerfile
|--requirements.txt

To run locally
`python -m venv venv`
`pip install -r requirements.txt`
`python app/main.py`

To run on docker
`docker build -t <_name_> .`
`docker run -it --net=host <_name_>`
