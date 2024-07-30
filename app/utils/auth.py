import os
import re
from typing import List
from db import run_db_transactions
from models.roles import Role
from models.users import User
import jwt
from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import SecurityScopes
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from fastapi import Request

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data_dict, expires_delta: timedelta | None = None):
    data_to_encode = data_dict.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=5)

    data_to_encode.update({"exp": expire})
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    encoded_jwt = jwt.encode(data_to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return encoded_jwt


def generate_user_dict_to_encode(user: User):
    role = run_db_transactions("get", {"role": user["role"]}, Role)
    # Current permission dict formart
    # {
    #     "entity": "User",
    #     "scope": "Data",
    #     "permission": "Read",
    #     "effect": "Allow"
    # }

    permissions_list: List[str] = []

    if type(role) is not type([]):
        return role

    for permission in role[0]["permissions"]:
        if permission["effect"] == "Allow":
            # Pass all permissions into a list with dict paramas seperated by "_"
            permissions_list.append(
                "{0}_{1}_{2}".format(
                    permission["entity"].lower(),
                    permission["scope"].lower(),
                    permission["permission"].lower(),
                )
            )

    return {
        "organization": user["parent_organization"],
        "type": user["user_type"],
        "role": user["role"],
        "scopes": permissions_list,
        "sub": user["email"],
    }


# Will check whether a user has the necessary permissions
# and retruns true otherwise it fails
async def user_has_permissions(security_scopes: SecurityScopes, request: Request):
    authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not authenticate values",
        headers={"Authorization": authenticate_value},
    )

    if not request.headers.get("Authorization"):
        return credentials_exception

    token = re.search("(?<=Bearer ).*", request.headers.get("Authorization")).group(0)

    try:
        JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
        JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception

        token_scopes = payload.get("scopes", [])

    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"Authorization": authenticate_value},
            )

    return True
