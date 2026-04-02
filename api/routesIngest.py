import logging as log
from fastapi import APIRouter, Depends, HTTPException

from api.auth import require_auth
from api.models import ErrorResponse, IngestRequest, IngestResponse
from Vector.Ingestion.pipeline import ingest_document

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post(
    "/file",
    response_model=IngestResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def ingest_file(payload: IngestRequest, _auth: dict = Depends(require_auth)):
    log.info(
        "Ingest request received",
        extra={"path_file": payload.path_file, "collection_name": payload.collection_name, "doc_id": payload.doc_id},
    )
    try:
        result = ingest_document(
            path_file=payload.path_file,
            collection_name=payload.collection_name,
            doc_id=payload.doc_id,
        )
        log.info("Ingest succeeded", extra={"doc_id": result.get("doc_id"), "collection": result.get("collection_name")})
        return IngestResponse(**result)
    except FileNotFoundError as exc:
        log.warning("Ingest failed: file not found", extra={"path_file": payload.path_file})
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        log.warning("Ingest failed: invalid input", extra={"path_file": payload.path_file, "error": str(exc)})
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        log.exception("Ingest failed with unexpected error")
        raise HTTPException(status_code=500, detail=f"Ingestion failure: {exc}")
