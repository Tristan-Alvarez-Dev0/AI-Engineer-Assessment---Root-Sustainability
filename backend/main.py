from typing import List, Annotated, Sequence

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from orm_models import AddressORM
from database import Base, engine, SessionLocal
from models import Address, AddressCreate, AddressesRefresh, AddressUpdate
from similarity import address_similarity
from mapbox_client import MapboxClient

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Address Assessment Backend",
    description="Minimal backend for the Root Sustainability AI/ML Engineer assessment.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DBSession = Annotated[Session, Depends(get_db_session)]
mapbox_client = MapboxClient()


def score(address: str, matched_address: str) -> float:
    similarity_score = address_similarity(address, matched_address)
    return similarity_score.score


def lookup_and_score(address: str) -> tuple:
    matched_address = mapbox_client.geocode_best_match(address)
    if matched_address is None:
        return "", 0

    similarity_score = score(address, matched_address)
    return matched_address, similarity_score


@app.get("/addresses", response_model=List[Address])
def get_addresses(session: DBSession) -> List[Address]:
    addresses: Sequence[AddressORM] = session.scalars(select(AddressORM)).all()
    return [address.to_pydantic() for address in addresses]


@app.get("/addresses/{id}", response_model=Address)
def get_address(session: DBSession, id: int) -> Address:
    address = session.scalars(select(AddressORM).where(AddressORM.id == id)).one_or_none()
    return address.to_pydantic()


@app.post("/addresses", response_model=Address, status_code=201)
def create_address(session: DBSession, payload: AddressCreate) -> Address:
    match, score = lookup_and_score(payload.address)
    session.add(address := AddressORM(address=payload.address, matched_address=match, match_score=score))
    session.commit()
    return address.to_pydantic()

@app.post("/addresses/refresh", status_code=200)
def refresh_addresses(session: DBSession, payload: AddressesRefresh):
    query =select(AddressORM)
    if payload.ids is not None:
        query.where(AddressORM.id.in_(payload.ids))
    addresses: Sequence[AddressORM] = session.scalars(query).all()
    for address in addresses:
        match, score = lookup_and_score(address.address)
        address.matched_address = match
        address.match_score = score
    session.commit()
    return [address.to_pydantic() for address in addresses]

@app.post("/addresses/{id}", response_model=Address, status_code=201)
def update_address(session: DBSession, id: int, payload: AddressUpdate) -> Address:
    address = session.scalars(select(AddressORM).where(AddressORM.id == id)).one_or_none()
    match, score = lookup_and_score(payload.address)
    address.address = payload.address
    address.matched_address = match
    address.match_score = score
    session.commit()
    return address.to_pydantic()

