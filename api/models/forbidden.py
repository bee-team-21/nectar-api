from pydantic import BaseModel, Field

class Forbidden(BaseModel):
    detail:str
    class Config:
        schema_extra = {
            "example": {"detail": "Not authenticated"},
        }