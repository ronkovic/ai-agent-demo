#!/usr/bin/env python
"""OpenAPI スキーマ生成スクリプト."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_platform.main import app

if __name__ == "__main__":
    openapi_schema = app.openapi()
    output_path = Path(__file__).parent.parent.parent / "openapi" / "openapi.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print(f"OpenAPI schema generated: {output_path}")
