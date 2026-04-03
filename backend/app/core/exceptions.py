from typing import Any, Dict, Optional

class BaseAppException(Exception):
    """Exception de base pour toute l'application ILM AI."""
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        location: str = "unknown",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.location = location
        self.details = details or {}
        super().__init__(self.message)

class LLMException(BaseAppException):
    """Erreurs liees aux modeles de langage (Ollama, OpenAI, RAG)."""
    def __init__(self, message: str, location: str = "llm_service", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=502, location=location, details=details)

class AuthException(BaseAppException):
    """Erreurs liees a l'authentification Clerk ou aux permissions Admin."""
    def __init__(self, message: str, location: str = "auth_service"):
        super().__init__(message, status_code=401, location=location)

class ResourceNotFoundException(BaseAppException):
    """Erreurs lancees lorsqu'une ressource (feedback, fichier) est manquante."""
    def __init__(self, message: str, location: str = "resource_manager"):
        super().__init__(message, status_code=404, location=location)

class ValidationException(BaseAppException):
    """Erreurs liees au format des données envoyées par le client."""
    def __init__(self, message: str, location: str = "validator"):
        super().__init__(message, status_code=422, location=location)
