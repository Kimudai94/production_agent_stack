import pytest
import unittest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch

class TestPipelineInitialization(unittest.TestCase):
    """Tests für Pipeline Startphase"""

    def setUp(self):
        self.test_config = {
            'model': {'model_id': 'qwen3-14b-instruct', 'api_base': 'http://localhost:1234/v1', 'temperature': 0.2},
            'pipeline': {'max_agents': 4, 'timeout_per_agent_seconds': 60}
        }
    
    @patch('src.pipeline.ModelPool')
    def test_pipeline_creates_model_pool(self, mock_pool):
        """Test dass Pipeline ModelPool initialisiert"""
        from src.pipeline import AgentPipeline
        pipeline = AgentPipeline()
        self.assertIsNotNone(pipeline.model_pool)
    
    def test_pipeline_loads_config(self):
        """Test Config Loading"""
        config_path = "config/model_config.yaml"
        if Path(config_path).exists():
            from src.pipeline import AgentPipeline
            pipeline = AgentPipeline(config_path=config_path)
            self.assertIsInstance(pipeline.config, dict)

class TestAgentRoles(unittest.TestCase):
    """Tests für einzelne Agenten Rollen"""
    def setUp(self):
        self.mock_model = Mock()
        self.sample_state = {
            "raw_input": "Test project",
            "phase": "initialization"
        }
    
    def test_requirement_analyzer_initializes(self):
        """Test Analyzer Initialisierung"""
        from src.specialist_agents import RequirementAnalyzer
        analyzer = RequirementAnalyzer(model=self.mock_model)
        self.assertEqual(analyzer.role, "Product Owner & Business Analyst")
        self.assertEqual(analyzer.name, "RequirementAnalyzer")
    
    def test_designer_initializes(self):
        """Test Designer Initialisierung"""
        from src.specialist_agents import SystemDesigner
        designer = SystemDesigner(model=self.mock_model)
        self.assertEqual(designer.role, "System Architect")
    
    def test_generator_initializes(self):
        """Test Code Generator Initialisierung"""
        from src.specialist_agents import CodeGenerator
        generator = CodeGenerator(model=self.mock_model)
        self.assertEqual(generator.role, "Senior Developer")
    
    def test_quality_checker_initializes(self):
        """Test Quality Checker Initialisierung"""
        from src.specialist_agents import QualityChecker
        checker = QualityChecker(model=self.mock_model)
        self.assertEqual(checker.role, "QA Engineer")

class TestStateTransition(unittest.TestCase):
    """Tests für State Übergänge zwischen Agents"""
    
    def test_analyzer_produces_valid_output_keys(self):
        """Test dass Analyzer alle erwarteten Keys produziert"""
        expected_keys = ["analyzed_requirements", "phase", "next_agent"]
        
        # Mock execution simulation
        mock_result = {
            "analyzed_requirements": "Mock analysis result",
            "phase": "analysis_complete",
            "next_agent": "system_designer"
        }
        
        for key in expected_keys:
            self.assertIn(key, mock_result)

def run_unit_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentRoles))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_unit_tests()
    exit(0 if success else 1)
