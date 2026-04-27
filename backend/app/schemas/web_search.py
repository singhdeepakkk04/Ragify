from pydantic import BaseModel
from typing import Literal

class WebResult(BaseModel):
    title: str
    url: str  
    snippet: str
    source: Literal["web"] = "web"
