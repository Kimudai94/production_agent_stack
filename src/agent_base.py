from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from smolagents import ToolCallingAgent, OpenAIServerModel
from rich.console import Console
from datetime import datetime

console = Console()

class SharedModelAgent(ABC):
    """
    Abstract Base für alle Agents im Pool.
    Teilt sich Model-Instanz über ModelPool.
    """
    
    def __init__(self, 
                 name: str,
                 role: str,
                 model: OpenAIServerModel,
                 tools: List = None,
                 max_steps: int = 10):
        self.name = name
        self.role = role
        self.model = model
        self.tools = tools or []
        self.max_steps = max_steps
        self.execution_log: List[Dict] = []
        console.print(f"[cyan]▶️  Agent created: {name} ({role})[/cyan]")
    
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Muss von Subklassen implementiert werden.
        Nimmt State entgegen, gibt neuen State zurück.
        """
        pass
    
    def _log_execution(self, task: str, success: bool, duration: float, output: Any = None):
        """Execution Logging für Debugging"""
        
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "success": success,
            "duration_seconds": round(duration, 2),
            "output_preview": str(output)[:200] if output else None
        })
    
    def run_agent_task(self, task_prompt: str, context: Dict = None) -> str:
        """Helper für Standard-Agent-Execution"""

        import time
        
        agent = ToolCallingAgent(
            name=self.name,
            model=self.model,
            tools=self.tools,
            max_steps=self.max_steps
        )
        
        console.print(f"[green]▶️  {self.name}: {task_prompt[:50]}...[/green]")
        
        start_time = time.time()
        try:
            result = agent.run(task_prompt, additional_args=context or {})
            duration = time.time() - start_time
            
            self._log_execution(task_prompt, True, duration, result)
            console.print(f"[green]✓  {self.name} completed in {duration:.1f}s[/green]")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self._log_execution(task_prompt, False, duration, str(e))
            console.print(f"[red]✗  {self.name} failed: {str(e)}[/red]")
            raise
