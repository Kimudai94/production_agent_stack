from pathlib import Path
from typing import Dict, Any, List, Optional
from smolagents import Tool
import subprocess
import shlex
import json

ALLOWED_COMMANDS = ['python', 'python3', 'pip', 'npm', 'node', 'npx', 'pytest', 
                    'flake8', 'black', 'mypy', 'git', 'ls', 'cat', 'mkdir',
                    'touch', 'rm', 'echo', 'grep', 'find', 'sed', 'awk']

BLOCKED_PATTERNS = ['rm -rf', 'sudo', 'chmod 777', 'mkfs',
                    'dd ', 'shutdown', 'reboot', ':(){:|:&};:']

class SafeShellTool(Tool):
    name = "safe_shell"
    description = "Führt sicheren Shell-Befehl aus (Whitelist-basiert)"
    inputs = {
        "command": {"type": "string", "description": "Auszuführender Befehl"},
        "working_dir": {"type": "string", "description": "Working Directory", "required": False},
        "timeout_seconds": {"type": "integer", "description": "Timeout in Sekunden", "required": False}
    }
    output_type = "string"
    
    def __init__(self, project_root: str):
        super().__init__()
        self.project_root = Path(project_root).resolve()
    
    def _validate_command(self, command: str) -> bool:
        """Überprüft ob Command erlaubt ist"""
        first_word = command.split()[0] if command.split() else ""
        if first_word not in ALLOWED_COMMANDS:
            raise PermissionError(f"Befehl nicht erlaubt: {first_word}")
        for pattern in BLOCKED_PATTERNS:
            if pattern in command:
                raise PermissionError(f"Gefährliches Pattern erkannt: {pattern}")
        return True
    
    def forward(self, command: str, working_dir: str = ".", timeout_seconds: int = 60) -> str:
        self._validate_command(command)
        cwd = (self.project_root / working_dir).resolve()
        
        try:
            result = subprocess.run(shlex.split(command), cwd=cwd, capture_output=True, text=True, timeout=timeout_seconds)
            output = {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode, "command": command}
            return json.dumps(output, indent=2)
        except subprocess.TimeoutExpired:
            return json.dumps({"error": f"Timeout nach {timeout_seconds}s"})
        except Exception as e:
            return json.dumps({"error": str(e)})
