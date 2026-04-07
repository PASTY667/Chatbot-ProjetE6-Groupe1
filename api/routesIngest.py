from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from api.auth import require_auth
from api.models import ErrorResponse, IngestRequest, IngestResponse
from api.storage import save_uploaded_file, resolve_collection_name
from Vector.Ingestion.pipeline import ingest_document

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post(
    "/file",
    response_model=IngestResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def ingest_file(payload: IngestRequest, _auth: dict = Depends(require_auth)):
    try:
        result = ingest_document(
            path_file=payload.path_file,
            collection_name=payload.collection_name,
            doc_id=payload.doc_id,
        )
        return IngestResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failure: {exc}")


@router.post(
    "/upload",
    response_model=IngestResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def ingest_upload(
    file: UploadFile = File(...),
    scope: str = Form("user"),
    chat_id: str | None = Form(None),
    collection_name: str | None = Form(None),
    doc_id: str | None = Form(None),
    _auth: dict = Depends(require_auth),
):
    try:
        saved_path = save_uploaded_file(file=file, scope=scope, chat_id=chat_id)
        effective_collection = resolve_collection_name(scope=scope, chat_id=chat_id, collection_name=collection_name)
        result = ingest_document(path_file=str(saved_path), collection_name=effective_collection, doc_id=doc_id)
        return IngestResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failure: {exc}")
