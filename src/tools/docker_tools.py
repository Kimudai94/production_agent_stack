from pathlib import Path
from typing import Dict, Any, List, Optional
from smolagents import Tool
import subprocess

class DockerBuildTool(Tool):
    name = "docker_build"
    description = "Buildet Docker Image aus Dockerfile"
    inputs = {
        "tag": {"type": "string", "description": "Image Tagname"},
        "context": {"type": "string", "description": "Build Context Pfad", "required": False},
        "dockerfile": {"type": "string", "description": "Pfad zum Dockerfile", "required": False}
    }
    output_type = "string"
    
    def forward(self, tag: str, context: str = ".", dockerfile: str = "Dockerfile") -> str:
        cmd = ['docker', 'build', '-t', tag, '-f', dockerfile, context]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return f"✓ Docker Image gebaut: {tag}"
        raise RuntimeError(f"Docker build failed:\n{result.stderr}")

class DockerRunTool(Tool):
    name = "docker_run"
    description = "Startet Docker Container"
    inputs = {
        "image": {"type": "string", "description": "Image Name"},
        "detach": {"type": "boolean", "description": "Im Hintergrund starten (-d)", "required": False},
        "ports": {"type": "string", "description": "Port Mapping (z.B. '8080:80')", "required": False},
        "env_vars": {"type": "string", "description": "Environment Variablen JSON", "required": False}
    }
    output_type = "string"
    
    def forward(self, image: str, detach: bool = True, ports: str = "", env_vars: str = "") -> str:
        cmd = ['docker', 'run']
        if detach:
            cmd.append('-d')
        if ports:
            cmd.extend(['-p', ports])
        if env_vars:
            import json
            env_dict = json.loads(env_vars)
            for k, v in env_dict.items():
                cmd.extend(['-e', f'{k}={v}'])
        cmd.append(image)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            container_id = result.stdout.strip()
            return f"✓ Container gestartet: {container_id[:12]}"
        raise RuntimeError(f"Docker run failed:\n{result.stderr}")
