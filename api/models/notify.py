from typing import Optional
from pydantic import BaseModel


class Notify(BaseModel):
    message: str = "Alert"
    file: Optional[str] = None
