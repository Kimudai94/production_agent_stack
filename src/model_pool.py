import threading
from typing import Dict, Optional
from contextlib import contextmanager
from smolagents import OpenAIServerModel
import logging

logger = logging.getLogger(__name__)

class ModelPool:
    """
    Thread-safe Singleton für geteilte Model-Instanz.
    Spart VRAM durch einmaliges Loading.
    """

    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._models: Dict[str, OpenAIServerModel] = {}
        self._session_counts: Dict[str, int] = {}
        self._lock = threading.RLock()
        self._initialized = True
        logger.info("Model Pool initialized (Singleton)")
    
    def get_model(self, 
                  model_id: str = "qwen3-14b-instruct",
                  api_base: str = "http://localhost:1234/v1",
                  temperature: float = 0.2,
                  **kwargs) -> OpenAIServerModel:
        """
        Holt oder erstellt Model-Instanz.
        max_tokens und andere zusätzliche Args werden ignoriert (nur für Logging).
        """

        cache_key = f"{model_id}:{temperature}"
        
        with self._lock:
            if cache_key not in self._models:
                logger.info(f"Creating new model instance: {model_id}")
                self._models[cache_key] = OpenAIServerModel(
                    model_id=model_id,
                    api_base=api_base,
                    api_key="lmstudio",
                    temperature=temperature
                )
                self._session_counts[cache_key] = 0
            
            self._session_counts[cache_key] += 1
            logger.debug(f"Session count for {model_id}: {self._session_counts[cache_key]}")
            return self._models[cache_key]
    
    @contextmanager
    def managed_session(self, model_id: str = "qwen3-14b-instruct", **kwargs):
        """
        Context Manager für sichere Sessions mit Auto-Cleanup.
        """

        model = self.get_model(model_id, **kwargs)
        
        try:
            yield model, model_id
        finally:
            with self._lock:
                cache_key = f"{model_id}:{kwargs.get('temperature', 0.2)}"
                if cache_key in self._session_counts:
                    self._session_counts[cache_key] -= 1
                    
                    if self._session_counts[cache_key] <= 0:
                        logger.info(f"Cleaning up unused model: {model_id}")
                        del self._models[cache_key]
                        del self._session_counts[cache_key]
    
    def get_stats(self) -> Dict:
        """VRAM und Session Statistik"""
        
        return {
            "active_models": len(self._models),
            "total_sessions": sum(self._session_counts.values()),
            "sessions_per_model": dict(self._session_counts)
        }
