"""
Provide implementation of health check controllers.
"""

from fastapi import APIRouter

router = APIRouter(prefix='/health', tags=['Health check'], include_in_schema=False)


@router.get('')
async def health():
    return {'status': 'ok'}
