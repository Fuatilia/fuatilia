from utils.auth import (
    create_access_token,
    generate_user_dict_to_encode,
    get_password_hash,
    verify_password,
)
from db import run_db_transactions
from models.users import User, UserCreationBody, UserUpdateBody, UserLoginBody


async def create_user(user_creation_body: UserCreationBody):
    password = user_creation_body.password
    user_creation_data = {**dict(user_creation_body)}

    del user_creation_data["password"]

    user_creation_data = {
        **dict(user_creation_data),
        "pass_hash": get_password_hash(password),
    }
    data = User(**user_creation_data)
    response = run_db_transactions("create", data, User)

    return response


async def update_user(user_update_body: UserUpdateBody):
    response = run_db_transactions(
        "update", user_update_body.model_dump(exclude_none=True), User
    )
    return response


async def filter_users(user_filter_body: any, page: int = 1, items_per_page: int = 5):
    user_filter_body["limit"] = items_per_page
    user_filter_body["page"] = page
    response = run_db_transactions("get", user_filter_body, User)

    return response


async def delete_user(id: str):
    data = {"id": id}
    response = run_db_transactions("delete", data, User)
    print(response)

    return response


async def login_user(login_body: UserLoginBody):
    user_list = await filter_users(
        {"email": login_body.email}
    )  # Should return an array

    if len(user_list) < 1:
        return {
            "status_code": 404,
            "message": "Invalid email/username or password",
            "error": "Missing details",
        }
    if len(user_list) > 1:
        return {
            "status_code": 404,
            "message": "Invalid email/username or password",
            "error": f"Invalid response count > 1 : {user_list}",
        }

    if not verify_password(login_body.password, user_list[0]["pass_hash"]):
        return {
            "status_code": 401,
            "message": "Invalid email/username or password",
            "error": "Missing details",
        }

    user_data = generate_user_dict_to_encode(user_list[0])
    if type(user_data) is not type([]) and user_data.get("status") in [500, 400]:
        return user_data

    jwt = create_access_token(user_data)

    return {"access_token": jwt, "token_type": "bearer"}
