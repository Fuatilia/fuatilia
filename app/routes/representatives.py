from services.representatives import create_representative, update_representative
from models.representatives import (
    RepresentativeCreationBody, 
    RepresentativeUpdateBody )
from fastapi import APIRouter


represenatives_router = APIRouter(
    tags=["Representatives"],
    prefix="/representatives"
)

@represenatives_router.post("/create")
async def createRepresentative(createBody: RepresentativeCreationBody ):
    return await create_representative(createBody)

@represenatives_router.patch("/update")
async def updateRepresentative(updateBody: RepresentativeUpdateBody ):
    return await update_representative(updateBody)


@represenatives_router.get("/{id}")
async def filter_representatives(id: str|None = None):
    return NotImplementedError

@represenatives_router.delete("/{id}")
async def delete_representative(id: str = None):
    return NotImplementedError
