import yaml
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from src.model_pool import ModelPool
from src.specialist_agents import (
    RequirementAnalyzer,
    SystemDesigner,
    CodeGenerator,
    QualityChecker
)

console = Console()

class AgentPipeline:
    """
    Orchestriert sequentielle Multi-Agent Ausführung.
    Model-Sharing über ModelPool.
    """

    def __init__(self, config_path: str = "config/agent_config.yaml"):
        self.config = self._load_config(config_path)
        self.model_pool = ModelPool()
        self.state: Dict[str, Any] = {}
        self.pipeline_start_time: datetime = None
        self.pipeline_end_time: datetime = None
        console.print("[bold blue]Pipeline initialized[/bold blue]")
    
    def _load_config(self, path: str) -> Dict:
        """Lädt YAML Konfiguration"""
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def _get_agent_by_role(self, role: str):
        """Holt passenden Agent basierend auf Rolle"""
        model = self.model_pool.get_model(**self.config['model'])
        
        agent_map = {
            "RequirementAnalyzer": RequirementAnalyzer,
            "SystemDesigner": SystemDesigner,
            "CodeGenerator": CodeGenerator,
            "QualityChecker": QualityChecker
        }
        
        agent_class = agent_map.get(role)
        if not agent_class:
            raise ValueError(f"Unknown agent role: {role}")
        
        return agent_class(model=model, tools=[])
    
    def run(self, initial_input: str) -> Dict[str, Any]:
        """Führt vollständige Pipeline aus."""
        self.pipeline_start_time = datetime.now()
        
        console.print(f"\n[bold]🚀 Starting Pipeline[/bold]\n")
        console.print(f"Input: {initial_input[:100]}{'...' if len(initial_input) > 100 else ''}\n")
        
        self.state = {
            "raw_input": initial_input,
            "started_at": self.pipeline_start_time.isoformat(),
            "current_phase": "initialization"
        }
        
        agent_sequence = [
            "RequirementAnalyzer",
            "SystemDesigner",
            "CodeGenerator",
            "QualityChecker"
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            for idx, role in enumerate(agent_sequence):
                task = progress.add_task(f"[cyan]{role}", total=100)
                
                try:
                    agent = self._get_agent_by_role(role)
                    self.state = agent.execute(self.state)
                    progress.update(task, completed=100)
                    console.print(f"[dim]→ Passed to next phase[/dim]\n")
                    
                except Exception as e:
                    console.print(f"[bold red]✗ Pipeline failed at {role}: {e}[/bold red]")
                    self.state["failed_at"] = role
                    self.state["error"] = str(e)
                    break
        
        self.pipeline_end_time = datetime.now()
        self.state["completed_at"] = self.pipeline_end_time.isoformat()
        self.state["pipeline_duration_seconds"] = (
            self.pipeline_end_time - self.pipeline_start_time
        ).total_seconds()
        self.state["model_pool_stats"] = self.model_pool.get_stats()
        
        self._save_results()
        self._print_summary()
        
        return self.state
    
    def _save_results(self):
        """Speichert Pipeline-Ergebnisse"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"pipeline_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False, default=str)
        
        console.print(f"\n[green]✓ Results saved to: {output_file}[/green]")
    
    def _print_summary(self):
        """Zeigt Pipeline-Summary"""
        console.print("\n" + "="*60)
        console.print("[bold]Pipeline Summary[/bold]")
        console.print("="*60)
        
        if self.state.get("completed"):
            console.print("[green]✓ Pipeline completed successfully[/green]")
        else:
            console.print("[yellow]⚠ Pipeline terminated early[/yellow]")
        
        console.print(f"\nDuration: {self.state.get('pipeline_duration_seconds', 0):.1f}s")
        console.print(f"Agents Executed: 4")
        console.print(f"Model Pool Stats: {self.model_pool.get_stats()}")
        console.print("="*60 + "\n")
