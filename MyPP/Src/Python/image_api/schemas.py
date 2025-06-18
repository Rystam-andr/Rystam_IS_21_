from pydantic import BaseModel, Field
from datetime import datetime

class ImageCreate(BaseModel):
    name: str = Field(..., description="Название изображения")
    file: bytes = Field(..., description="Данные файла изображения")
    
class ImageInfo(BaseModel):
    name: str
    size: int
    width: int
    height: int
    type: str
    date_added: datetime
    
class RenameImage(BaseModel):
    new_name: str
    
class ImageResponse(BaseModel):
    id: int
    name: str
    size: int
    width: int
    height: int
    type: str
    date_added: datetime
    
    class Config:
        orm_mode = True
