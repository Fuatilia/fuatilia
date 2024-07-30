import os
from utils.auth import user_has_permissions
from fastapi import Security
from services.files import file_upload, get_file_data, stream_file_data
from utils.enum_utils import FileType
from models.bills import BillCreationBody, BillUpdateBody
from models.files import FileUploadBody
from services.bills import (
    create_bill,
    delete_bill,
    filter_bills,
    get_bills_files_list,
    update_bill,
)

from fastapi import APIRouter
from fastapi.responses import StreamingResponse


bill_router = APIRouter(tags=["Bills"], prefix="/bills")


@bill_router.post("/create")
async def createBill(
    createBody: BillCreationBody,
    permission_check_passed=Security(
        user_has_permissions, scopes=["bill_data_create"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return await create_bill(createBody)
    else:
        return permission_check_passed


@bill_router.patch("/update")
async def updateBill(
    updateBody: BillUpdateBody,
    permission_check_passed=Security(
        user_has_permissions, scopes=["bill_data_update"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return await update_bill(updateBody)
    else:
        return permission_check_passed


@bill_router.get("")
async def filterBillsBy(
    title: str | None = None,
    status: str | None = None,
    sponsored_by: str | None = None,
    supported_by: str | None = None,
    summary: str | None = None,
    summary_created_by: str | None = None,
    summary_upvoted_by: str | None = None,
    summary_downvoted_by: str | None = None,
    final_date_voted: str | None = None,
    topics_in_the_bill: str | None = None,
    file_url: str | None = None,
    created_at: str | None = None,
    updated_at: str | None = None,
    page: int = 1,
    items_per_page: int = 10,
):
    filter_params = {
        "title": title,
        "status_code": status,
        "sponsored_by": sponsored_by,
        "supported_by ": supported_by,
        "summary": summary,
        "summary_created_by": summary_created_by,
        "summary_upvoted_by": summary_upvoted_by,
        "summary_downvoted_by": summary_downvoted_by,
        "final_date_voted": final_date_voted,
        "topics_in_the_bill": topics_in_the_bill,
        "file_url": file_url,
        "created_at": created_at,
        "updated_at": updated_at,
        "page": page,
        "items_per_page": items_per_page,
    }

    return await filter_bills(filter_params)


@bill_router.get("/{id}")
async def filterBillsById(id: str | None = None):
    return await filter_bills({"id": id})


@bill_router.delete("/{id}")
async def deleteBill(
    id: str = None,
    permission_check_passed=Security(
        user_has_permissions, scopes=["bill_data_delete"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return await delete_bill(id)
    else:
        return permission_check_passed


@bill_router.get("/file/{id}")
async def getBillFiles(id, file_name: str):
    return await get_file_data(
        os.environ.get("BILLS_DATA_BUCKET_NAME"), f"{id}/{file_name}"
    )


@bill_router.get("/files/list")
async def getBillFilesList(fileType: FileType, house: str = None):
    return await get_bills_files_list(fileType, house)


@bill_router.get("/file/{id}/playback")
async def streamBillFiles(id, start_KB: int, stop_KB: int, file_name: str):
    return StreamingResponse(
        await stream_file_data(f"{id}/{file_name}", start_KB, stop_KB)
    )


@bill_router.post("/upload")
async def uploadBillFiles(
    file_type: FileType,
    fileUploadBody: FileUploadBody,
    permission_check_passed=Security(
        user_has_permissions, scopes=["bill_data_delete"], use_cache=True
    ),
):
    if permission_check_passed is True:
        return await file_upload(
            os.environ.get("BILLS_DATA_BUCKET_NAME"),
            file_type,
            fileUploadBody.file_name,
            fileUploadBody.base64encoding,
        )

    else:
        return permission_check_passed
