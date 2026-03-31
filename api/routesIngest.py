from fastapi import APIRouter, Depends, HTTPException

from api.authorization import Principal, require_permission
from api.collection_policy import resolve_ingest_collection
from api.models import ErrorResponse, IngestRequest, IngestResponse
from Vector.Ingestion.pipeline import ingest_document

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post(
    "/file",
    response_model=IngestResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def ingest_file(
    payload: IngestRequest,
    principal: Principal = Depends(require_permission("ingest:user")),
):
    try:
        # enforce mapping server-side
        collection_name = resolve_ingest_collection(principal, payload.target)

        result = ingest_document(
            path_file=payload.path_file,
            collection_name=collection_name,
            doc_id=payload.doc_id,
        )
        return IngestResponse(**result)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failure: {exc}")