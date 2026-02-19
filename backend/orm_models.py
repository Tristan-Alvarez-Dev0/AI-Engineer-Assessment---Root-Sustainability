from sqlalchemy import Column, Integer, String, Float

from database import Base

class AddressORM(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    matched_address = Column(String, nullable=True)
    match_score = Column(Float, nullable=True)

    def to_pydantic(self):
        from models import Address
        return Address(id=self.id, address=self.address, matched_address=self.matched_address, match_score=self.match_score)