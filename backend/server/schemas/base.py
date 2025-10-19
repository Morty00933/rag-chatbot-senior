from pydantic import BaseModel, ConfigDict

class Orm(BaseModel):
    model_config = ConfigDict(from_attributes=True)