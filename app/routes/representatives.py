import os
from services.files import (
    file_upload, get_file_data,
    stream_file_data
    )
from models.files import FileUploadBody
from services.representatives import (
    create_representative, delete_representative, 
    filter_representatives, get_representative_files_list, 
    update_representative, 
    )
from models.representatives import (
    RepresentativeCreationBody, 
    RepresentativeUpdateBody )
from utils.enum_utils import FileType
from fastapi import APIRouter
from fastapi.responses import StreamingResponse


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

@represenatives_router.get("")
async def filterRepresentativesBy(
        full_name : str|None = None, 
        position : str|None = None, 
        position_type : str|None = None, 
        house : str|None = None, 
        area_represented : str|None = None, 
        phone_number : str|None = None, 
        image_url : str|None = None, 
        gender : str|None = None, 
        created_at_start : str | None = None,
        created_at_end : str | None = None,
        updated_at_start : str | None = None,
        updated_at_end : str | None = None,
        page: int = 1, items_per_page: int = 10 
    ):


    filter_params = {
        'full_name' : full_name,
        'position' : position,
        'position_type' : position_type,
        'house' : house,
        'area_represented' : area_represented,
        'phone_number' : phone_number,
        'image_url' : image_url,
        'gender' : gender,
        'created_at_start' : created_at_start,
        'created_at_end' : created_at_end,
        'updated_at_start' : updated_at_start,
        'updated_at_end' : updated_at_end,
        'page': page, 
        'items_per_page': items_per_page 

    }

    return await filter_representatives(filter_params)

@represenatives_router.get("/{id}")
async def filterRepresentativesById(id: str|None = None):
    return await filter_representatives({"id":id})

@represenatives_router.delete("/{id}")
async def deleteRepresentative(id: str = None):
    return await delete_representative(id)

@represenatives_router.get('/files/list/{id}')
async def getRepresentativeFilesList(id, file_type:FileType):
    return await get_representative_files_list(id, file_type)

@represenatives_router.get('/{id}/file')
async def getRepresentativeFiles(id, file_name:str):
    return await get_file_data(os.environ.get('REPS_DATA_BUCKET_NAME'),
                               f'{id}/{file_name}')

@represenatives_router.get('/file/{id}/playback')
async def streamRepresentativeFiles(id, 
                                    start_KB:int, 
                                    stop_KB:int, 
                                    file_name:str 
                                    ):
    return  StreamingResponse(await stream_file_data(os.environ.get('REPS_DATA_BUCKET_NAME'),
                                                     f'{id}/{file_name}', 
                                                     start_KB, 
                                                     stop_KB
                                                     )
                                                )

@represenatives_router.post('/{id}/upload/{file_type}')
async def uploadRepresentatveFiles(id:str, 
                                   file_type: FileType, 
                                   fileUploadBody:FileUploadBody 
                                   ):
    return await file_upload(os.environ.get('REPS_DATA_BUCKET_NAME'),
                                file_type, 
                                fileUploadBody.file_name, 
                                fileUploadBody.base64encoding,
                                id = id
                                )