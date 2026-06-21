from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/live")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def readiness(request: Request) -> JSONResponse:
    checks = {"database": False, "redis": False}

    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        pass

    try:
        checks["redis"] = bool(request.app.state.redis_client.ping())
    except Exception:
        pass

    ready = all(checks.values())
    return JSONResponse(
        {"status": "ok" if ready else "unavailable", "checks": checks},
        status_code=(
            status.HTTP_200_OK
            if ready
            else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
    )
