# import standard modules
import os
# from importlib.metadata import version

# import third party modules
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# import project related modules
from src.feedme_service.service.views import (frontend, record)


service_name = "feedme-service"

app = FastAPI(title=service_name) #, version=version(service_name))

static_path = os.path.join(os.getcwd(), "src/feedme_service/service/static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(frontend.router)
app.include_router(record.router)
