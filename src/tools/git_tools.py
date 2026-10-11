from pathlib import Path
from typing import Dict, Any, List, Optional
from smolagents import Tool
import subprocess

class GitInitTool(Tool):
    name = "git_init"
    description = "Initialisiert neues Git Repository"
    inputs = {"branch_name": {"type": "string", "description": "Name für initialen Branch", "required": False}}
    output_type = "string"
    
    def forward(self, branch_name: str = "main") -> str:
        result = subprocess.run(['git', 'init', '-b', branch_name], capture_output=True, text=True)
        if result.returncode == 0:
            return f"✓ Git Repository initialisiert (Branch: {branch_name})"
        raise RuntimeError(f"Git init failed: {result.stderr}")

class GitAddTool(Tool):
    name = "git_add"
    description = "Fügt Dateien zum Git Index hinzu"
    inputs = {"files": {"type": "string", "description": "Dateipfade oder Pattern"}}
    output_type = "string"
    
    def forward(self, files: str = ".") -> str:
        result = subprocess.run(['git', 'add', files], capture_output=True, text=True)
        if result.returncode == 0:
            return f"✓ Dateien hinzugefügt: {files}"
        raise RuntimeError(f"Git add failed: {result.stderr}")

class GitCommitTool(Tool):
    name = "git_commit"
    description = "Führt Git Commit durch"
    inputs = {
        "message": {"type": "string", "description": "Commit Nachricht"},
        "all": {"type": "boolean", "description": "Alle geänderten Dateien automatisch hinzufügen", "required": False}
    }
    output_type = "string"
    
    def forward(self, message: str, all: bool = True) -> str:
        cmd = ['git', 'commit', '-m', message]
        if all:
            cmd.insert(2, '-a')
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return f"✓ Commit erfolgreich: {message}"
        raise RuntimeError(f"Git commit failed: {result.stderr}")

class GitStatusTool(Tool):
    name = "git_status"
    description = "Zeigt aktuellen Git Status"
    inputs = {"short": {"type": "boolean", "description": "Kurzformat", "required": False}}
    output_type = "string"
    
    def forward(self, short: bool = False) -> str:
        flag = "--short" if short else ""
        result = subprocess.run(['git', 'status', flag], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        raise RuntimeError(f"Git status failed: {result.stderr}")
