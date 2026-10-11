import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from rich.console import Console
import logging

console = Console()
logger = logging.getLogger(__name__)

@dataclass
class Checkpoint:
    id: str
    timestamp: str
    step_name: str
    state: Dict[str, Any]
    metadata: Dict[str, Any]

class CheckpointManager:
    """Speichert und verwende Pipeline-Zustände für Recovery."""

    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.current_checkpoint: Optional[Checkpoint] = None
        self.history: List[str] = []
    
    def _generate_checkpoint_id(self) -> str:
        """Erzeugt eindeutige ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    def save_checkpoint(self, step_name: str, state: Dict[str, Any], metadata: Dict[str, Any] = None) -> Checkpoint:
        """Erstellt persistenten Snapshot des States."""
        checkpoint_id = self._generate_checkpoint_id()
        timestamp = datetime.now().isoformat()
        safe_state = self._sanitize_state(state)
        
        checkpoint = Checkpoint(
            id=checkpoint_id,
            timestamp=timestamp,
            step_name=step_name,
            state=safe_state,
            metadata=metadata or {}
        )
        
        filepath = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(checkpoint), f, indent=2, ensure_ascii=False, default=str)
        
        self.history.append(checkpoint_id)
        self.current_checkpoint = checkpoint
        
        logger.info(f"Checkpoint saved: {checkpoint_id} at {step_name}")
        console.print(f"[dim]✓ Checkpoint created: {checkpoint_id}[/dim]")
        
        return checkpoint
    
    def restore_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """Lädt Zustand vom Checkpoint zurück."""
        filepath = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Checkpoint nicht gefunden: {checkpoint_id}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        checkpoint = Checkpoint(**data)
        self.current_checkpoint = checkpoint
        
        logger.info(f"Checkpoint restored: {checkpoint_id}")
        console.print(f"[green]✓ Restored checkpoint: {checkpoint_id}[/green]")
        
        return checkpoint.state
    
    def rollback_to(self, checkpoint_id: str) -> Dict[str, Any]:
        """Kehrt zu Checkpoint zurück und löscht spätere."""
        state = self.restore_checkpoint(checkpoint_id)
        
        later_checkpoints = [cp for cp in self.history if cp > checkpoint_id]
        for cp_id in later_checkpoints:
            filepath = self.checkpoint_dir / f"{cp_id}.json"
            if filepath.exists():
                filepath.unlink()
        
        self.history = [cp for cp in self.history if cp <= checkpoint_id]
        
        return state
    
    def list_checkpoints(self) -> List[Dict[str, str]]:
        """Zeigt alle verfügbaren Checkpoints"""
        checkpoints = []
        
        for filepath in sorted(self.checkpoint_dir.glob("*.json")):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            checkpoints.append({
                "id": data["id"],
                "timestamp": data["timestamp"],
                "step_name": data["step_name"]
            })
        
        return checkpoints
    
    def _sanitize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Entfernt nicht-seriable Daten aus State"""
        sanitized = {}
        
        for key, value in state.items():
            if isinstance(value, str) and len(value) > 50000:
                sanitized[key] = value[:50000] + f"...[{len(value)} chars]"
            elif isinstance(value, datetime):
                sanitized[key] = value.isoformat()
            else:
                try:
                    json.dumps(value)
                    sanitized[key] = value
                except TypeError:
                    sanitized[key] = f"<unserializable: {type(value).__name__}>"
        
        return sanitized
    
    def cleanup_old_checkpoints(self, keep_last: int = 5):
        """Löscht alte Checkpoints"""
        if len(self.history) <= keep_last:
            return
        
        to_delete = self.history[:-keep_last]
        
        for cp_id in to_delete:
            filepath = self.checkpoint_dir / f"{cp_id}.json"
            if filepath.exists():
                filepath.unlink()
                self.history.remove(cp_id)
        
        console.print(f"[dim]Cleaned up {len(to_delete)} old checkpoints[/dim]")

    def create_automatic_checkpoint(self, step_name: str, state: Dict[str, Any], frequency: str = "every_step") -> Optional[Checkpoint]:
        """
        Erstellt Checkpoint basierend auf Strategie.
        Frequenzen: "never", "every_step", "on_success", "on_failure"
        """
        if frequency == "never":
            return None
        elif frequency == "every_step":
            return self.save_checkpoint(step_name, state)
        elif frequency == "on_success":
            if state.get("completed"):
                return self.save_checkpoint(step_name, state, {"auto": "success"})
        elif frequency == "on_failure":
            if state.get("error"):
                return self.save_checkpoint(step_name, state, {"auto": "failure"})
        
        return None
    
    def get_latest_checkpoint(self) -> Optional[Checkpoint]:
        """Holt neuesten Checkpoint"""
        if not self.history:
            return None
        
        latest_id = self.history[-1]
        return self.restore_checkpoint(latest_id)
