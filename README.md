# Production Agent Stack

Lokale Agentic AI Entwicklung für RTX 4080 (16GB VRAM)

## Voraussetzungen

- LM Studio (Port 1234)
- Python 3.10+
- NVIDIA RTX 4080 mit aktuellen Treibern

## Quick Start

```bash
# 1. Dependencies
pip install -r requirements.txt

# 2. LM Studio Server starten
lms load qwen3-14b
lms server start --port 1234

# 3. Test Pipeline
python -m src.main --example

# 4. Tests
python -m run_tests.sh
