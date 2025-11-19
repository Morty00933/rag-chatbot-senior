from fastapi import APIRouter

router = APIRouter()


@router.post("/reindex", tags=["admin"])
async def reindex() -> dict[str, bool | str]:
    # Заглушка; позднее добавим реальную переиндексацию
    return {"ok": True, "message": "reindex scheduled"}
