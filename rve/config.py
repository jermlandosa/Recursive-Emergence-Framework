import os


def get_db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    data_dir = os.getenv("RVE_DATA_DIR", ".")
    os.makedirs(data_dir, exist_ok=True)
    return f"sqlite:///{os.path.join(data_dir, 'rve_ledger.db')}"


def env_bool(name: str, default=False) -> bool:
    val = os.getenv(name, str(default)).lower()
    return val in ("1", "true", "yes", "on")

