import time
import uuid

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

EMAIL = "23f1000212@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-cs5l60.example.com"

app = FastAPI()

# CORS MUST be added before custom middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


class HeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        response.headers["X-Request-ID"] = str(uuid.uuid4())
        response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"

        return response


app.add_middleware(HeaderMiddleware)


@app.get("/")
async def home():
    return {"status": "ok"}


@app.get("/stats")
async def stats(values: str = Query(...)):
    nums = [int(x.strip()) for x in values.split(",")]

    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums),
    }
