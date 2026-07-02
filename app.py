
import os,time,uuid,yaml,jwt
from dotenv import load_dotenv
from fastapi import FastAPI,Query,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel

load_dotenv()

EMAIL="23f1000212@ds.study.iitm.ac.in"
ALLOWED_ORIGIN="https://dash-cs5l60.example.com"
ISSUER="https://idp.exam.local"
AUDIENCE="tds-v2xo2a50.apps.exam.local"
PUBLIC_KEY="""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

app=FastAPI()

app.add_middleware(CORSMiddleware,
 allow_origins=[ALLOWED_ORIGIN],
 allow_methods=["*"],
 allow_headers=["*"],
 allow_credentials=False)

class MW(BaseHTTPMiddleware):
    async def dispatch(self,request,call_next):
        s=time.perf_counter()
        r=await call_next(request)
        r.headers["X-Request-ID"]=str(uuid.uuid4())
        r.headers["X-Process-Time"]=f"{time.perf_counter()-s:.6f}"
        return r
app.add_middleware(MW)

@app.get("/")
def root():
    return {"status":"ok"}

@app.get("/stats")
def stats(values:str=Query(...)):
    nums=[int(x.strip()) for x in values.split(",")]
    return {"email":EMAIL,"count":len(nums),"sum":sum(nums),
            "min":min(nums),"max":max(nums),"mean":sum(nums)/len(nums)}

class Token(BaseModel):
    token:str

@app.post("/verify")
def verify(body:Token):
    try:
        p=jwt.decode(body.token,PUBLIC_KEY,algorithms=["RS256"],issuer=ISSUER,audience=AUDIENCE)
        return {"valid":True,"email":p.get("email"),"sub":p.get("sub"),"aud":p.get("aud")}
    except Exception:
        return JSONResponse(status_code=401,content={"valid":False})

DEFAULTS={"port":8000,"workers":1,"debug":False,"log_level":"info","api_key":"default-secret-000"}

def b(v): return str(v).lower() in ("true","1","yes","on")
def c(k,v):
    if k in ("port","workers"): return int(v)
    if k=="debug": return b(v)
    return str(v)

@app.get("/effective-config")
def effective_config(set:list[str]|None=Query(None)):
    cfg=DEFAULTS.copy()
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml") as f:
            y=yaml.safe_load(f) or {}
            for k,v in y.items(): cfg[k]=c(k,v)
    for k,v in os.environ.items():
        if k=="NUM_WORKERS": cfg["workers"]=int(v)
        if k.startswith("APP_"):
            kk=k[4:].lower()
            cfg[kk]=c(kk,v)
    if set:
        for item in set:
            if "=" in item:
                k,v=item.split("=",1)
                cfg[k]=c(k,v)
    cfg["api_key"]="****"
    return cfg
