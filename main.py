import time
import uuid

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

EMAIL = "23f1000212@ds.study.iitm.ac.in"

ALLOWED_ORIGIN = "https://dash-cs5l60.example.com"

app = FastAPI()


class HeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        elapsed = time.perf_counter() - start

        response.headers["X-Request-ID"] = str(uuid.uuid4())
        response.headers["X-Process-Time"] = f"{elapsed:.6f}"

        return response


app.add_middleware(HeaderMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return {"message": "FastAPI Statistics Service Running"}


@app.get("/stats")
async def stats(values: str = Query(...)):
    try:
        nums = [int(i.strip()) for i in values.split(",") if i.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid integer list")

    if len(nums) == 0:
        raise HTTPException(status_code=400, detail="No values supplied")

    total = sum(nums)

    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / len(nums),
    }