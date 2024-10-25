import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse

from src.api.v1.base import api_router
from src.core.auth import get_current_user
from src.core.config import settings
from src.models import User


app = FastAPI(
    title=settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(api_router, prefix='/api/v1')

@app.get("/ping")
async def ping(user: User = Depends(get_current_user)) -> dict:
    return {'message': 'Pong'}


if __name__ == '__main__':
    host = settings.project_host
    uvicorn.run(
        'main:app',
        host=str(settings.project_host),
        port=settings.project_port,
        reload=True,
    )
