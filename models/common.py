# models/common.py

from pydantic import BaseModel, ConfigDict, Field,AfterValidator,PlainSerializer
from bson import ObjectId
from typing import Annotated

# --- Pydantic v2 ve üzeri için ObjectId'yi işlemenin modern ve önerilen yöntemi ---

def validate_object_id(v: any) -> ObjectId:
    """ObjectId'yi doğrular"""
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")

# PyObjectId artık bir sınıf değil, Pydantic'in anlayacağı şekilde "açıklanmış" bir tip.
# AfterValidator: Gelen veriyi ObjectId'ye çevirir.
# PlainSerializer: ObjectId'yi dışarıya (JSON'a) verirken string'e çevirir.
PyObjectId = Annotated[
    ObjectId,
    AfterValidator(validate_object_id),
    PlainSerializer(lambda x: str(x), return_type=str),
]

# MongoBaseModel'de bir değişiklik yok, aynı kalıyor.
class MongoBaseModel(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )