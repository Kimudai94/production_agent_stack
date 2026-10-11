# Neue Lumo-Session starten

1. GitHub-Repository teilen:
   
   "Lumo, hier ist mein Projekt: https://github.com/DEIN_USER/production-agent-stack"

2. Kurze Status-Angabe (Copy/Paste aus README):
   
   "Erster Pipeline-Lauf erfolgreich. Nächste Ziele: Tools aktivieren, MCP einrichten, eigene Use-Cases testen."

3. Falls Probleme auftauchen:
   - Log-Fragmente als Text posten
   - Spezifische Frage stellen

.

.

# 🎯 Priorisierte Roadmap für production_agent_stack

Hier ist eine strukturierte Liste aller möglichen Erweiterungen, sortiert nach **Impact × Aufwand**.

---

## 🔴 **Priority 1: Kritische Optimierungen** (Sofort angehen)

### **1. Tools aktiv in Agents einbinden**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🔴 Hoch |
| **Aufwand** | 2-4 Stunden |
| **Wert** | Agent wird *handlungsfähig* statt nur Text generieren |

**Umsetzung:**
```python
# src/specialist_agents.py - CodeGenerator.__init__() ändern:

from pathlib import Path
from src.tools.file_tools import FileReaderTool, FileWriterTool, FileListerTool
from src.tools.git_tools import GitAddTool, GitCommitTool, GitStatusTool
from src.tools.shell_tools import SafeShellTool

project_root = str(Path.cwd())

self.tool_list = [
    FileReaderTool(project_root=project_root),
    FileWriterTool(project_root=project_root),
    FileListerTool(project_root=project_root),
    GitAddTool(),
    GitCommitTool(),
    GitStatusTool(),
    SafeShellTool(project_root=project_root),
]

super().__init__(
    name="CodeGenerator",
    role="Senior Developer",
    model=model,
    tools=self.tool_list,  # ← Echte Tools statt []
    max_steps=15
)
```

**Test:**
```bash
python -m src.main --input "Erstelle eine test.txt mit 'Hello World'"
# Prüfen ob Datei wirklich erstellt wird
```

---

### **2. Error Recovery & Retry-Logik**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🔴 Hoch |
| **Aufwand** | 3-5 Stunden |
| **Wert** | Pipeline bricht nicht bei erstem Fehler ab |

**Umsetzung:**
```python
# src/pipeline.py erweitern:

class FaultTolerantPipeline(AgentPipeline):
    def run_with_retry(self, initial_input: str, max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                return self.run(initial_input)
            except Exception as e:
                if attempt == max_retries - 1:
                    console.print(f"[red]All retries failed: {e}[/red]")
                    raise
                
                console.print(f"[yellow]Retry {attempt+1}/{max_retries}...[/yellow]")
                
                # Zu letztem Checkpoint rollbacken
                latest_cp = self.checkpoint_manager.get_latest_checkpoint()
                if latest_cp:
                    self.state = self.checkpoint_manager.restore_checkpoint(latest_cp.id)
```

---

### **3. VRAM-Monitoring im Live-Betrieb**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🔴 Hoch |
| **Aufwand** | 1 Stunde |
| **Wert** | Verhindert OOM-Crashes bei langen Pipelines |

**Umsetzung:**
```bash
# Terminal 2 parallel zur Pipeline:
python -m src.vram_monitor

# Oder kurz vor Pipeline-Start prüfen:
python -c "
import subprocess
output = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.used,memory.free', '--format=csv'])
print(output.decode())
"
```

**Integration in main.py:**
```python
def pre_flight_check(self):
    """Vor Pipeline-Start VRAM prüfen"""
    total, used = get_nvidia_gpu_memory()
    available = total - used
    
    if available < 5000:  # <5GB frei
        console.print("[red]⚠️ Warnung: Weniger als 5GB VRAM verfügbar![/red]")
        console.print("Model könnte nicht laden oderOOM-Crash auftreten.")
        return False
    return True
```

---

## 🟡 **Priority 2: Core Feature-Erweiterungen**

### **4. Parallelisierung für 2 Agenten gleichzeitig**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🟡 Mittel |
| **Aufwand** | 4-6 Stunden |
| **Wert** | 20-30% Zeitersparnis bei bestimmten Tasks |

**Umsetzung:**
```python
# src/pipeline.py erweitern:

def run_parallel_phases(self):
    """Parallel: Design + Requirements können gleichzeitig laufen"""
    from concurrent.futures import ThreadPoolExecutor
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Parallel: Analyzer und Designer
        future_analysis = executor.submit(self._run_agent, "RequirementAnalyzer")
        future_design = executor.submit(self._run_agent, "SystemDesigner")
        
        # Warten auf beide
        state_analysis = future_analysis.result()
        state_design = future_design.result()
        
        # Merge States
        self.state = {**state_analysis, **state_design}
```

**Voraussetzung:** 24GB+ VRAM ODER sorgfältiges Model-Sharing

---

### **5. Context Compression für längere Pipelines**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🟡 Mittel |
| **Aufwand** | 3-5 Stunden |
| **Wert** | Verhindert Token-Limit-Probleme bei komplexen Projekten |

**Umsetzung:**
```python
# src/context_compressor.py neu:

from typing import Dict, Any

class ContextCompressor:
    def compress(self, state: Dict[str, Any], max_tokens: int = 32000) -> Dict[str, Any]:
        """Kürzt große Strings, behält Meta-Informationen"""
        compressed = {}
        
        for key, value in state.items():
            if isinstance(value, str) and len(value) > 50000:
                # Nur wichtige Abschnitte behalten
                lines = value.split('\n')
                compressed[key] = '\n'.join(lines[:500] + ['...'] + lines[-100:])
            else:
                compressed[key] = value
        
        return compressed
```

---

### **6. Logging-Verbesserung (Structured Logs)**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🟡 Mittel |
| **Aufwand** | 1-2 Stunden |
| **Wert** | Debugging wird viel einfacher |

**Umsetzung:**
```python
# config/logging_config.yaml:

logging:
  level: INFO
  format: "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
  handlers:
    - type: file
      path: logs/pipeline.log
      rotation: "10 MB"
    - type: console
      colorize: true
```

```python
# src/main.py:

import logging
import logging.handlers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🟢 **Priority 3: Integrationen**

### **7. MCP Server voll aktivieren**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🟢 Niedrig |
| **Aufwand** | 4-8 Stunden |
| **Wert** | Erweiterte Tools (Datenbank, Cloud APIs) |

**Umsetzung:**
```bash
# 1. Node.js installieren
winget install OpenJS.NodeJS.LTS

# 2. MCP Server installieren
npx -y @modelcontextprotocol/server-database postgresql://user:pass@localhost/db
npx -y @modelcontextprotocol/server-slack

# 3. config/mcp_servers.yaml anpassen
servers:
  - name: database
    command: "npx"
    args:
      - "-y"
      - "@modelcontextprotocol/server-database"
      - "postgresql://..."
    enabled: true
```

---

### **8. VS Code Integration**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🟢 Niedrig |
| **Aufwand** | 2-4 Stunden |
| **Wert** | Direkt im Editor arbeiten |

**Umsetzung:**
```json
// .vscode/tasks.json:

{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Agent Pipeline",
      "type": "shell",
      "command": "python -m src.main --input ${input:userInput}",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always"
      }
    }
  ]
}
```

---

### **9. Claude Code Frontend vollständig einbinden**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🟢 Niedrig |
| **Aufwand** | 1-2 Stunden |
| **Wert** | Interaktive Sessions statt Batch-Jobs |

**Umsetzung:**
```bash
# .env aktualisieren:

ANTHROPIC_BASE_URL=http://localhost:1234/v1
ANTHROPIC_API_KEY=lmstudio

# .claude.json erstellen:
cat > ~/.claude.json << 'EOF'
{
  "hasCompletedOnboarding": true,
  "primaryApiKey": "sk-no-key-required"
}
EOF

# CLAUDE.md im Projekt:
cat > CLAUDE.md << 'EOF'
# production_agent_stack

Du bist ein Coding-Agent für dieses lokale AI-Stack Projekt.

## Tools
- LM Studio Server läuft auf Port 1234
- Model: qwen3-14b-instruct
- Python smolagents Framework

## Regeln
- Teste jeden Code vor Commit
- Nutze Checkpoints regelmäßig
- Dokumentiere Änderungen
EOF

# Starten:
claude --model qwen3-14b-instruct
```

---

## 🔵 **Priority 4: Langfristige Verbesserungen**

### **10. Custom Agents entwickeln**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🔵 Niedrig |
| **Aufwand** | 4-8 Stunden pro Agent |
| **Wert** | Domänenspezifische Expertise |

**Beispiel-Agenten:**

```python
# SecurityAuditor:
class SecurityAuditor(SharedModelAgent):
    def execute(self, state):
        code = state.get("generated_code", "")
        task = """Performe Security Review..."""
        # SQL Injection, XSS, Secrets prüfen
        ...

# PerformanceOptimizer:
class PerformanceOptimizer(SharedModelAgent):
    def execute(self, state):
        # Profiling durchführen, Bottlenecks finden
        ...

# DocumentationWriter:
class DocumentationWriter(SharedModelAgent):
    def execute(self, state):
        # API Docs, README, Kommentare schreiben
        ...
```

---

### **11. Benchmark-Suite erweitern**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🔵 Niedrig |
| **Aufwand** | 3-5 Stunden |
| **Wert** | Objektive Performance-Messung |

**Umsetzung:**
```python
# src/testing/benchmark_suite.py erweitern:

class FullBenchmarkSuite:
    TASKS = [
        ("Simple Function", "Write fibonacci function", 5),
        ("REST API", "Create FastAPI with CRUD", 25),
        ("Full Project", "Build React app with backend", 60),
    ]
    
    def measure(self):
        for name, prompt, expected_minutes in self.TASKS:
            start = time.time()
            result = pipeline.run(prompt)
            duration = time.time() - start
            
            print(f"{name}: {duration:.1f}s (expected: {expected_minutes*60}s)")
```

---

### **12. Containerisierung & CI/CD**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🔵 Niedrig |
| **Aufwand** | 6-10 Stunden |
| **Wert** | Reproduzierbare Umgebungen |

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "src.main", "--example"]
```

**GitHub Actions (.github/workflows/ci.yml):**
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: python -m src.testing.pipeline_tests
```

---

### **13. Model Fine-Tuning auf eigenen Code**
| Metrik | Wert |
|--------|------|
| **Priorität** | 🔵 Niedrig |
| **Aufwand** | 10-20 Stunden (+ GPU Hours) |
| **Wert** | Bessere Ergebnisse für deine Codebase |

**Umsetzung:**
```bash
# Dataset sammeln:
# - Deine alten Projekte
# - Code Reviews
# - Docstrings

# Fine-Tuning mit Unsloth/Liger Kernel:
pip install unsloth
python fine_tune_qwen.py --dataset my_code_dataset --epochs 3
```

---

## 🗓️ **Empfohlene Woche-für-Woche Planung**

### **Woche 1: Stabilität**
- Tag 1-2: ✅ **Tools aktivieren** (Critical!)
- Tag 3: ✅ **Error Recovery** implementieren
- Tag 4: ✅ **VRAM Monitoring** einrichten
- Tag 5: Tests aller neuen Features

### **Woche 2: Verbesserte UX**
- Tag 1-2: Logging-Verbesserungen
- Tag 3-4: Context Compression
- Tag 5: Claude Code Integration testen

### **Woche 3: Erweiterte Features**
- Tag 1-3: MCP Server aktivieren
- Tag 4-5: Erste Custom Agents (SecurityAuditor)

### **Woche 4: Produktion**
- Tag 1-2: Benchmark-Suite erweitern
- Tag 3-4: Docker Containerisierung
- Tag 5: CI/CD Pipeline

---