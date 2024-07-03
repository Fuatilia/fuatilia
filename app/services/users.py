from utils.auth import get_password_hash
from db import run_db_transactions
from models.users import User, UserCreationBody, UserUpdateBody


async def create_user(user_creation_body: UserCreationBody):
    password = user_creation_body.password
    user_creation_data = {**dict(user_creation_body)}

    del user_creation_data["password"]

    user_creation_data = {
        **dict(user_creation_data),
        'pass_hash' : get_password_hash(password)
        }
    data  = User(**user_creation_data)
    response = run_db_transactions('create',data, User)

    return response


async def update_user(user_id:str, user_update_body: UserUpdateBody):

    data  = User(**dict(user_update_body))
    response = run_db_transactions('update',user_update_body.model_dump(exclude_none=True),User)
    print(response)

    return response


async def filter_users(user_filter_body: any, page:int=1, items_per_page:int=5):
    user_filter_body['limit'] = items_per_page
    response = run_db_transactions('get',user_filter_body, User)

    return response


async def delete_user(id: str):
    data  = {"id":id}
    response = run_db_transactions('delete',data, User)
    print(response)

    return response



