from pathlib import Path
from typing import Dict, Any, List, Optional
from smolagents import Tool
import json

class FileReaderTool(Tool):
    name = "file_reader"
    description = "Liest Inhalt von Dateien im Projektverzeichnis"
    inputs = {
        "filepath": {"type": "string", "description": "Relativer Pfad"},
        "max_lines": {"type": "integer", "description": "Maximale Zeilen", "required": False}
    }
    output_type = "string"
    
    def __init__(self, project_root: str):
        super().__init__()
        self.project_root = Path(project_root).resolve()
    
    def forward(self, filepath: str, max_lines: int = 200) -> str:
        target_path = (self.project_root / filepath).resolve()
        
        if not str(target_path).startswith(str(self.project_root)):
            raise PermissionError(f"Path außerhalb von Projekt Root: {filepath}")
        
        if not target_path.exists():
            raise FileNotFoundError(f"Datei nicht gefunden: {filepath}")
        
        content = target_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        if len(lines) > max_lines:
            preview = '\n'.join(lines[:max_lines])
            return f"{preview}\n\n...[{len(lines) - max_lines} Zeilen ausgellassen]..."
        
        return content

class FileWriterTool(Tool):
    name = "file_writer"
    description = "Schreibt Inhalt in Datei mit automatischem Backup"
    inputs = {
        "filepath": {"type": "string", "description": "Pfad zur Datei"},
        "content": {"type": "string", "description": "Inhalt zu schreiben"},
        "create_dirs": {"type": "boolean", "description": "Parent Verzeichnisse erstellen", "required": False}
    }
    output_type = "string"
    
    def __init__(self, project_root: str):
        super().__init__()
        self.project_root = Path(project_root).resolve()
    
    def forward(self, filepath: str, content: str, create_dirs: bool = True) -> str:
        target_path = (self.project_root / filepath).resolve()
        
        if not str(target_path).startswith(str(self.project_root)):
            raise PermissionError(f"Path außerhalb von Projekt Root: {filepath}")
        
        if target_path.exists():
            backup_path = target_path.with_suffix('.bak')
            backup_path.write_text(target_path.read_text(), encoding='utf-8')
        
        if create_dirs:
            target_path.parent.mkdir(parents=True, exist_ok=True)
        
        target_path.write_text(content, encoding='utf-8')
        
        return f"✓ Datei geschrieben: {filepath} ({len(content)} bytes)"

class FileListerTool(Tool):
    name = "file_lister"
    description = "Listet Dateien in Verzeichnis mit Filter"
    inputs = {
        "path": {"type": "string", "description": "Verzeichnispfad", "required": False},
        "pattern": {"type": "string", "description": "Glob Pattern", "required": False},
        "recursive": {"type": "boolean", "description": "Rekursiv durchsuchen", "required": False}
    }
    output_type = "string"
    
    def __init__(self, project_root: str):
        super().__init__()
        self.project_root = Path(project_root).resolve()
    
    def forward(self, path: str = ".", pattern: str = "*", recursive: bool = True) -> str:
        target_path = (self.project_root / path).resolve()
        
        if not str(target_path).startswith(str(self.project_root)):
            raise PermissionError(f"Path außerhalb von Projekt Root: {path}")
        
        if not target_path.exists():
            raise FileNotFoundError(f"Verzeichnis nicht gefunden: {path}")
        
        if recursive:
            files = list(target_path.rglob(pattern))
        else:
            files = list(target_path.glob(pattern))
        
        rel_paths = [str(f.relative_to(self.project_root)) for f in files]
        
        return f"Found {len(files)} files:\n" + "\n".join(sorted(rel_paths))
