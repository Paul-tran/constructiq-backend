from pydantic import BaseModel
from typing import Optional


class SystemLevelConfigOut(BaseModel):
    id: int
    project_id: int
    level1_name: str
    level2_name: str
    level3_name: str

    class Config:
        from_attributes = True


class SystemLevelConfigUpdate(BaseModel):
    level1_name: Optional[str] = None
    level2_name: Optional[str] = None
    level3_name: Optional[str] = None


class SystemDisciplineCreate(BaseModel):
    name: str
    code: str


class SystemDisciplineOut(BaseModel):
    id: int
    project_id: int
    name: str
    code: str

    class Config:
        from_attributes = True


class SystemGroupCreate(BaseModel):
    name: str
    code: str


class SystemGroupOut(BaseModel):
    id: int
    discipline_id: int
    name: str
    code: str

    class Config:
        from_attributes = True


class SystemSubgroupCreate(BaseModel):
    name: str
    code: str


class SystemSubgroupOut(BaseModel):
    id: int
    group_id: int
    name: str
    code: str

    class Config:
        from_attributes = True
