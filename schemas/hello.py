from pydantic import BaseModel, Field


class HelloResponse(BaseModel):
    """Odpowiedź z endpointu hello"""
    message: str = Field(..., description="Spersonalizowany komunikat powitalny")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello John",
            }
        }

