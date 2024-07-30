import os
from utils.logger import logger
import dotenv
from fastapi import FastAPI
import uvicorn
from routes.users import user_router
from routes.votes import vote_router
from routes.representatives import represenatives_router
from routes.bills import bill_router
from routes.roles import role_router
from routes.custom_permissions import permission_router
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware


dotenv.load_dotenv()


app = FastAPI(
    title="Fuatilia",
    summary="Fuatilia API endpoints",
    version=os.environ.get("VERSION"),
    servers=[
        {"url": os.environ.get("DEV_BASE_URL") + "/api", "description": "Dev"},
        {"url": os.environ.get("SANDBOX_BASE_URL") + "/api", "description": "Sandbox"},
    ],
    docs_url="/docs/dev",
    redoc_url="/docs/api",
    openapi_url="/docs/fuatilia postman collection.json",
    root_path="/api",
)

# app.add_middleware(HTTPSRedirectMiddleware)
# app.add_middleware(
#     TrustedHostMiddleware, allowed_hosts=['*.fuatilia.africa']
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["....myfrontend...."],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

default_path_version = os.environ.get("DEFAULT_PATH_VERSION")
app.include_router(bill_router, prefix=default_path_version)
app.include_router(permission_router, prefix=default_path_version)
app.include_router(represenatives_router, prefix=default_path_version)
app.include_router(role_router, prefix=default_path_version)
app.include_router(user_router, prefix=default_path_version)
app.include_router(vote_router, prefix=default_path_version)

if __name__ == "__main__":
    is_dev = os.environ.get("ENVIRONMENT") == "dev"
    logger.info(
        {"host": os.environ.get("APP_HOST"), "port": os.environ.get("APP_PORT")}
    )
    uvicorn.run(
        "main:app",
        host=os.environ.get("APP_HOST"),
        port=int(os.environ.get("APP_PORT")),
        reload=is_dev,
    )
