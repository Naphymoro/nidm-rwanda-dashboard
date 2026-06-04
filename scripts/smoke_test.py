from __future__ import annotations

import io
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix=".tmp-smoke-", dir=ROOT, ignore_cleanup_errors=True) as temp:
        os.environ["NDIM_DESKTOP"] = "1"
        os.environ["NDIM_DATA_DIR"] = temp
        os.environ["NDIM_MAX_UPLOAD_MB"] = "5"
        os.environ.pop("DATABASE_URL", None)

        from fastapi.testclient import TestClient
        from pypdf import PdfWriter

        from app.main import app
        from app.storage import make_full_backup, verify_backup_archive

        client = TestClient(app)

        assert client.get("/api/status").status_code == 200
        health = client.get("/health").json()
        assert health["offline_ready"] is True
        assert client.get("/offline/status").json()["internet_required"] is False

        csv_data = b"narrative_id,text,country,admin_unit,source_type\nsmoke-1,People fear the pressure cooker but trust the health worker,Rwanda,Musanze,csv\n"
        csv_response = client.post("/ingest/csv", files={"file": ("stories.csv", csv_data, "text/csv")})
        assert csv_response.status_code == 200, csv_response.text
        assert csv_response.json()[0]["narrative_id"] == "smoke-1"

        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        pdf_buffer = io.BytesIO()
        writer.write(pdf_buffer)
        pdf_response = client.post("/ingest/pdf", files={"file": ("blank.pdf", pdf_buffer.getvalue(), "application/pdf")})
        assert pdf_response.status_code == 200, pdf_response.text

        encode_response = client.post("/encode?mode=manual&provider=deterministic", json=csv_response.json())
        assert encode_response.status_code == 200, encode_response.text

        backup = make_full_backup()
        verification = verify_backup_archive(backup)
        assert verification["valid"] is True

    print("NDIM production smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
