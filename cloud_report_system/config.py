from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    COHERE_API_KEY: str
    
    # Model settings
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    EMBEDDING_MODEL: str = "embed-english-light-v3.0"
    
    # System settings
    MAX_INPUT_LENGTH: int = 5000
    MAX_OUTPUT_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    
    class Config:
        env_file = ".env"
        extra = 'ignore'

settings = Settings()
