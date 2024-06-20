from fastapi import APIRouter

from models.votes import VoteCreationBody

vote_router = APIRouter(
    tags=["Vote"],
    prefix="/votes"
)

@vote_router.post("/create")
async def createVote(createBody: VoteCreationBody ):
    return NotImplementedError

@vote_router.get("/{id}")
async def filterUsers(id: str|None = None):
    return NotImplementedError