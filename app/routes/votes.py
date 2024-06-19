from fastapi import APIRouter


from models.votes import VoteCreationBody

vote_router = APIRouter(
    tags=["Vote"],
    prefix="/votes"
)
