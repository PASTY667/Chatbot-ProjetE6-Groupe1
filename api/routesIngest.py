# api/routesIngest.py
from fastapi import APIRouter, HTTPException
from api.models import IngestRequest, IngestResponse
from Vector.Ingestion.pipeline import ingest_document

router = APIRouter(prefix="/ingest",tags=["ingest"])

@router.post("/file",response_model=IngestResponse)
def ingest_file(payload: IngestRequest):
    try:
        result = ingest_document(
            path_file=payload.path_file,
            collection_name=payload.collection_name,
            doc_id=payload.doc_id,
        )
        return IngestResponse(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ingestion error : {e}")

