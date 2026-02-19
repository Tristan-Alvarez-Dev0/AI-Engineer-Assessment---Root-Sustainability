from typing import List, Optional
from pydantic import BaseModel


class Address(BaseModel):
    id: int
    address: str
    matched_address: Optional[str]
    match_score: float


class AddressCreate(BaseModel):
    address: str

class AddressUpdate(BaseModel):
    address: str


class AddressesRefresh(BaseModel):
    ids: Optional[List[int]]
