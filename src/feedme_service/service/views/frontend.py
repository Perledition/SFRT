
# import third party modules
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request

# import project related modules
from src.feedme_service.settings import templates


router = APIRouter(
    prefix="/view",
    tags=["view"],
)


@router.get("/recording", response_class=HTMLResponse, include_in_schema=False)
async def signup(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})