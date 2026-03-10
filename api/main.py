from api import models  # local API models
from api import routesChat, routesIngest  # local route modules
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
def root():
    """
    Health check endpoint for the LLM backend API.

    This route is used by the LAMP web server or monitoring probes to verify
    that the FastAPI service running on the LLM VM is reachable.

    :return: A simple JSON payload confirming the service is alive.
    :rtype: dict
    """
    return {"message": "Hello World"}
