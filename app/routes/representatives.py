from models.representatives import (
    RepresenativeImageUpdate, RepresentativeCreationBody, 
    RepresentativeUpdateBody )
from fastapi import APIRouter


represenatives_router = APIRouter(
    tags=["Representatives"],
    prefix="/representatives"
)

@represenatives_router.post("/create")
async def create_representative(createBody: RepresentativeCreationBody ):
    return NotImplementedError

@represenatives_router.patch("/update")
async def update_representative(updateBody: RepresentativeUpdateBody ):
    return await NotImplementedError


@represenatives_router.put("/update/image")
async def update_representative_image(updateBody: RepresenativeImageUpdate ):
    return await NotImplementedError

@represenatives_router.get("/{id}")
async def filter_representatives(id: str|None = None):
    return NotImplementedError

@represenatives_router.delete("/{id}")
async def delete_representative(id: str = None):
    return NotImplementedError
