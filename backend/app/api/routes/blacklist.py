from fastapi import APIRouter, HTTPException, Response, status

from app.repositories import security_repository
from app.schemas.blacklist import BlacklistCreateRequest


router = APIRouter(tags=["blacklist"])


@router.get("/blacklist")
def list_blacklist() -> dict:
    return {"items": security_repository.list_blacklist()}


@router.post("/blacklist", status_code=status.HTTP_201_CREATED)
def create_blacklist_entry(request: BlacklistCreateRequest) -> dict:
    item = security_repository.upsert_blacklist_entry(request.model_dump())
    return {"item": item}


@router.delete("/blacklist/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blacklist_entry(entry_id: int) -> Response:
    deleted = security_repository.delete_blacklist_entry(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Blacklist entry not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
