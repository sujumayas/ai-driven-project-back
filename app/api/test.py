from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["test"])

@router.get("/health")
async def test_health():
    """Simple health check for testing purposes."""
    return {"status": "ok", "message": "Test endpoint working"}

@router.post("/echo")
async def echo_charter(data: dict):
    """Echo back charter data for testing."""
    return {
        "received": data,
        "message": "Charter received successfully",
        "parsed": True
    }
