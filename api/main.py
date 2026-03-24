from api import models  # local API models
from api import routesChat, routesIngest  # local route modules
import Backend.Config.settings as settings
import utils.logger as logger
import logging as log
from Vector.Ingestion.pipeline import ingest_document, add_documents,ensure_collection,build_chroma_payloads
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

@app.post("api/v1/admin/ingest")
def ingest():
    """


    :return: Json payload containing :
    {
      "status": "ok",
      "scope": "company",
      "collection_name": "company_docs",
      "doc_id": "company_123_abcd",
      "chunks_count": 42,
      "inserted_id_count": 42
    }
    """
    pass