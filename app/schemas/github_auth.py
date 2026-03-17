"""
Схемы для GitHub OAuth авторизации
"""
from pydantic import BaseModel, Field


class GitHubAuthRequest(BaseModel):
    """Запрос на авторизацию через GitHub"""
    code: str = Field(..., description="Код авторизации полученный от GitHub")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "github_authorization_code_here"
                }
            ]
        }
    }
