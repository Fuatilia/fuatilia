import os
from utils.enum_utils import FileType
from models.files import FileUploadBody
from services.files import file_upload, get_file_data, stream_file_data
from services.votes import (
    create_vote,
    delete_vote,
    filter_votes,
    get_votes_files_list,
    update_vote,
)
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models.votes import VoteCreationBody, VoteUpdateBody

vote_router = APIRouter(tags=["Vote"], prefix="/votes")


@vote_router.post("/create")
async def createVote(createBody: VoteCreationBody):
    return await create_vote(createBody)


@vote_router.patch("/update")
async def updateVote(updateBody: VoteUpdateBody):
    return await update_vote(updateBody)


@vote_router.get("")
async def filterVotesBy(
    bill_id: str | None = None,
    representative_id: str | None = None,
    house: str | None = None,
    vote: str | None = None,
    vote_type: str | None = None,
    vote_summary: str | None = None,
    page: int = 1,
    items_per_page: int = 10,
):
    filter_params = {
        "bill_id": bill_id,
        "representative_id": representative_id,
        "house": house,
        "vote": vote,
        "vote_type": vote_type,
        "vote_summary": vote_summary,
        "page": page,
        "items_per_page": items_per_page,
    }

    return await filter_votes(filter_params)


@vote_router.get("/{id}")
async def filterVotesById(id: str | None = None):
    return await filter_votes({"id": id})


@vote_router.delete("/{id}")
async def deleteVote(id: str = None):
    return await delete_vote(id)


@vote_router.get("/files/list")
async def getVoteFilesList(file_type: FileType, house: str = None):
    return await get_votes_files_list(file_type, house)


@vote_router.get("/file/{id}")
async def getVoteFiles(id, file_name: str):
    return await get_file_data(
        os.environ.get("VOTES_DATA_BUCKET_NAME"), f"{id}/{file_name}"
    )


@vote_router.get("/file/{id}/playback")
async def streamVoteFiles(id, start_KB: int, stop_KB: int, file_name: str):
    return StreamingResponse(
        await stream_file_data(f"{id}/{file_name}", start_KB, stop_KB)
    )


@vote_router.post("/upload")
async def uploadVoteFiles(file_type: FileType, fileUploadBody: FileUploadBody):
    return await file_upload(
        os.environ.get("VOTES_DATA_BUCKET_NAME"),
        file_type,
        fileUploadBody.file_name,
        fileUploadBody.base64encoding,
    )
