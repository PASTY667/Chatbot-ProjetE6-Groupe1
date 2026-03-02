import models
import routesChat
import routesIngest
import Backend.Config.settings as settings
import utils.logger as logger
import logging as log
import os
import json
from fastapi import FastAPI, HTTPException

logger.get_logger()
log.info("Main reached")

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World"}
