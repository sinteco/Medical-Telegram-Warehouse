from pydantic import BaseModel

class MedicalProduct(BaseModel):
    id: int
    name: str
    price: float
    channel: str

    class Config:
        from_attributes = True
