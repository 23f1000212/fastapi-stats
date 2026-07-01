import os
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# -----------------------------
# Load .env
# -----------------------------
load_dotenv()

app = FastAPI(title="12-Factor Config Service")

# -----------------------------
# Enable CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Default configuration
# -----------------------------
DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# -----------------------------
# Helper functions
# -----------------------------
def to_bool(value):
    return str(value).strip().lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


def coerce(key, value):
    if key in ("port", "workers"):
        return int(value)

    if key == "debug":
        return to_bool(value)

    return str(value)


# -----------------------------
# Endpoint
# -----------------------------
@app.get("/effective-config")
def effective_config(set: list[str] | None = Query(default=None)):

    config = DEFAULTS.copy()

    # -------------------------
    # YAML layer
    # -------------------------
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml", "r") as f:
            yaml_config = yaml.safe_load(f) or {}

        for key, value in yaml_config.items():
            config[key] = coerce(key, value)

    # -------------------------
    # .env layer
    # -------------------------
    for key, value in os.environ.items():

        if key == "NUM_WORKERS":
            config["workers"] = int(value)

        elif key in config:
            config[key] = coerce(key, value)

    # -------------------------
    # APP_* environment variables
    # -------------------------
    for key, value in os.environ.items():

        if key.startswith("APP_"):

            actual_key = key[4:].lower()

            config[actual_key] = coerce(actual_key, value)

    # -------------------------
    # CLI overrides
    # -------------------------
    if set:

        for item in set:

            if "=" not in item:
                continue

            key, value = item.split("=", 1)

            config[key] = coerce(key, value)

    # -------------------------
    # Mask secret
    # -------------------------
    config["api_key"] = "****"

    return config


@app.get("/")
def home():
    return {
        "message": "12-Factor Config Service Running"
    }
