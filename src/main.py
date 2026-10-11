import argparse
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from datetime import datetime

from src.pipeline import AgentPipeline
from src.model_pool import ModelPool
from src.checkpoint_manager import CheckpointManager
from src.mcp.mcp_client import MCPClient

console = Console()
load_dotenv()

class ProductionPipeline(AgentPipeline):
    """Erweiterte Pipeline mit allen Features"""

    def __init__(self, config_path: str = "config/model_config.yaml"):
        super().__init__(config_path)
        self.checkpoint_manager = CheckpointManager()
        self.mcp_client = MCPClient()
        self.base_tools = []
        self._setup_base_tools()
    
    def _setup_base_tools(self):
        """Initialisiert Basis-Tools"""
        project_root = Path.cwd()
        
        from src.tools.file_tools import FileReaderTool, FileWriterTool, FileListerTool
        from src.tools.git_tools import GitAddTool, GitCommitTool, GitStatusTool
        from src.tools.shell_tools import SafeShellTool
        
        self.base_tools = [
            FileReaderTool(project_root=str(project_root)),
            FileWriterTool(project_root=str(project_root)),
            FileListerTool(project_root=str(project_root)),
            GitAddTool(),
            GitCommitTool(),
            GitStatusTool(),
            SafeShellTool(project_root=str(project_root)),
        ]
    
    def run_with_checkpoints(self, initial_input: str, auto_checkpoint: bool = True) -> Dict[str, Any]:
        """Führt Pipeline mit automatischen Checkpoints aus."""
        self.pipeline_start_time = datetime.now()
        self.state = {"raw_input": initial_input}
        
        agent_sequence = ["RequirementAnalyzer", "SystemDesigner", "CodeGenerator", "QualityChecker"]
        
        for idx, role in enumerate(agent_sequence):
            try:
                agent = self._get_agent_by_role(role)
                agent.tools = self.base_tools.copy()
                self.state = agent.execute(self.state)
                
                if auto_checkpoint:
                    self.checkpoint_manager.create_automatic_checkpoint(
                        step_name=role,
                        state=self.state,
                        frequency="on_success"
                    )
            except Exception as e:
                console.print(f"[bold red]✗ Failed at {role}: {e}[/bold red]")
                
                # Biete Recovery an
                available = self.checkpoint_manager.list_checkpoints()
                if available:
                    console.print(f"[yellow]Available checkpoints: {len(available)}[/yellow]")
                    console.print("Use --restore <checkpoint_id> to recover")
                
                self.state["failed_at"] = role
                self.state["error"] = str(e)
                break
        
        self.pipeline_end_time = datetime.now()
        self.state["completed_at"] = self.pipeline_end_time.isoformat()
        self.state["pipeline_duration_seconds"] = (
            self.pipeline_end_time - self.pipeline_start_time
        ).total_seconds()
        self.state["model_pool_stats"] = self.model_pool.get_stats()
        
        self._print_production_summary()
        return self.state
    
    def _print_production_summary(self):
        """Zeigt ausführliches Summary"""
        console.print(Panel(
            f"[bold]Production Run Summary[/bold]\n\n"
            f"Duration: {self.state.get('pipeline_duration_seconds', 0):.1f}s\n"
            f"Checkpoints: {len(self.checkpoint_manager.history)}\n"
            f"Model Pool Stats: {self.model_pool.get_stats()}",
            title="Pipeline Complete",
            border_style="green"
        ))

def main():
    parser = argparse.ArgumentParser(description="Production Agent Pipeline")
    parser.add_argument("--example", "-e", action="store_true")
    parser.add_argument("--input", "-i", type=str, default=None)
    parser.add_argument("--config", "-c", type=str, default="config/model_config.yaml")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--mcp", action="store_true", help="Enable MCP servers")
    
    args = parser.parse_args()
    
    if args.test:
        console.print("[cyan]Running Unit Tests...[/cyan]")
        from src.testing.pipeline_tests import run_unit_tests
        success = run_unit_tests()
        sys.exit(0 if success else 1)
    
    console.print(Panel(
        "[bold magenta]🚀 Production Agent Pipeline 2026[/bold magenta]\n"
        f"GPU: RTX 4080 (16GB VRAM)\n"
        f"Model: Qwen3 14B (Shared Model Pool)\n"
        f"Features: Checkpoints • MCP • Tools • Security",
        title="[bold]Startup[/bold]"
    ))
    
    pipeline = ProductionPipeline(config_path=args.config)
    
    if args.example:
        request = "Erstelle REST API für Bookshelf App mit CRUD"
    elif args.input:
        request = args.input
    else:
        request = "Erstelle Python FastAPI Projekt mit SQLAlchemy"
    
    result = pipeline.run_with_checkpoints(request, auto_checkpoint=True)
    
    console.print(Panel(
        f"[bold]Final Deliverable[/bold]\n"
        f"Phase: {result.get('phase', 'unknown')}\n"
        f"Output: See output/ directory",
        border_style="blue"
    ))

if __name__ == "__main__":
    main()
