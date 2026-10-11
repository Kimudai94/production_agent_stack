from src.agent_base import SharedModelAgent
from typing import Dict, Any

class RequirementAnalyzer(SharedModelAgent):
    """Analysiert Anforderungen und erstellt User Stories"""

    def __init__(self, model, tools=None):
        super().__init__(
            name="RequirementAnalyzer",
            role="Product Owner & Business Analyst",
            model=model,
            tools=tools or [],
            max_steps=5
        )
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiert Anforderungen aus Input"""

        task = f"""
        Analysiere folgende Anforderung und erstelle strukturierte Spezifikation:
        
        {state.get('raw_input', '')}
        
        Gib zurück:
        1. Klare Projektbeschreibung
        2. Liste von User Stories mit Acceptance Criteria
        3. Technische Stack Empfehlung
        4. Risikoidentifikation
        """
        
        result = self.run_agent_task(task, {"context": state})
        
        return {
            **state,
            "analyzed_requirements": result,
            "phase": "analysis_complete",
            "next_agent": "system_designer"
        }

class SystemDesigner(SharedModelAgent):
    """Erstellt Architektur-Design basierend auf Anforderungen"""

    def __init__(self, model, tools=None):
        super().__init__(
            name="SystemDesigner",
            role="System Architect",
            model=model,
            tools=tools or [],
            max_steps=7
        )
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert Architektur-Dokumentation"""
        
        requirements = state.get("analyzed_requirements", "")
        
        task = f"""
        Erstelle technische Architektur basierend auf diesen Anforderungen:
        
        {requirements}
        
        Gib zurück:
        1. Komponenten-Diagramm (ASCII Art)
        2. Datenbank-Schema
        3. API Endpoints Definition
        4. Security Überlegungen
        5. Deployment Plan
        """
        
        result = self.run_agent_task(task, {"requirements": state})
        
        return {
            **state,
            "architecture": result,
            "phase": "design_complete",
            "next_agent": "code_generator"
        }

class CodeGenerator(SharedModelAgent):
    """Generiert Code basierend auf Architektur"""

    def __init__(self, model, tools=None):
        super().__init__(
            name="CodeGenerator",
            role="Senior Developer",
            model=model,
            tools=tools or [],
            max_steps=15
        )
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert Produktions-Code"""

        architecture = state.get("architecture", "")
        
        task = f"""
        Implementiere basierend auf folgender Architektur:
        
        {architecture}
        
        Gib zurück:
        1. Verzeichnis-Struktur
        2. Quellcode für jede Komponente
        3. Unit Tests für kritische Funktionen
        4. README mit Setup-Anleitung
        """
        
        result = self.run_agent_task(task, {"architecture": state})
        
        return {
            **state,
            "generated_code": result,
            "phase": "coding_complete",
            "next_agent": "quality_checker"
        }

class QualityChecker(SharedModelAgent):
    """Reviewt Code und schreibt Tests"""

    def __init__(self, model, tools=None):
        super().__init__(
            name="QualityChecker",
            role="QA Engineer",
            model=model,
            tools=tools or [],
            max_steps=10
        )
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Performt Code Review und Test-Erweiterung"""

        code = state.get("generated_code", "")
        
        task = f"""
        Review den generierten Code und erweitere die Test-Suite:
        
        {code}
        
        Gib zurück:
        1. Code Review mit Schwachstellen
        2. Missing Test Cases
        3. Performance Optimierungen
        4. Finaler Status Report
        """
        
        result = self.run_agent_task(task, {"code": state})
        
        return {
            **state,
            "review_report": result,
            "phase": "final",
            "completed": True,
            "final_deliverable": self._compile_final_output(state)
        }
    
    def _compile_final_output(self, state: Dict) -> Dict:
        """Fasst alle Ergebnisse zusammen"""
        
        return {
            "requirements": state.get("analyzed_requirements"),
            "architecture": state.get("architecture"),
            "implementation": state.get("generated_code"),
            "quality_report": state.get("review_report"),
            "pipeline_metrics": {
                "agents_executed": 4,
                "phases_completed": ["analysis", "design", "coding", "review"]
            }
        }
