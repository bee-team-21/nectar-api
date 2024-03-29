from typing import List, Optional
from pydantic import BaseModel

class RequestBody(BaseModel):
    url:str

class Tag(BaseModel):
    name:str
    score: float
    flg_cage: Optional[bool] = False
    flg_animal: Optional[bool] = False

class DetectedObjects(BaseModel):
    name:str
    confidence:float
    flg_animal: Optional[bool] = False

class Captions(BaseModel):
    text : str
    confidence:float

class Risk(BaseModel):
    grade: str
    confidence: float

class AnalysisResult(BaseModel):
    user_id : str
    image_url: str
    tags:List[Tag]
    detected_objects : List[DetectedObjects]
    captions:Optional[List[Captions]]
    risk: List[Risk]
    text: str
    text_en:str
    

    