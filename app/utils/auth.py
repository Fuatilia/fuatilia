import os
import jwt
import random
import string
import logging
import datetime
from apps.users.models import User
from rest_framework import authentication
from rest_framework import exceptions
from argon2 import PasswordHasher
from drf_spectacular.extensions import OpenApiAuthenticationExtension

logger = logging.getLogger("app_logger")

HASH_SECRET_STR = os.environ.get("HASH_SECRET_STR")


def get_tokens_for_user(user: User):
    iat = datetime.datetime.now()
    exp_time = iat + datetime.timedelta(minutes=60)
    exp_epoch = int(exp_time.timestamp())
    data = {
        "username": user.username,
        "id": str(user.id),
        "role": user.role,
        "user_type": user.user_type,
        "organisation": user.parent_organization,
        "exp": exp_epoch,
        "iat": int(iat.timestamp()),
    }

    token = jwt.encode(data, HASH_SECRET_STR, algorithm="HS512")

    return {"access": str(token), "exp": exp_epoch}


def verify_user_token(token: str, user: User):
    logger.info(f"Verifying user token for {user.id}")
    try:
        decoded_data = jwt.decode(token, HASH_SECRET_STR, algorithms=["HS512"])
    except Exception as e:
        logger.exception(e)
        logger.error(f"Failed to verify user token for {user.id}")
        return {"verified": False, "error": e.__str__()}

    if decoded_data.get("username") != user.username:
        logger.error(f"Failed to verify user token for {user.id}")
        return {"verified": False, "error": "Invalid user token"}

    logger.info(f"Verified user token for {user.id}")
    return {"verified": True}


def create_client_id_and_secret(username: str):
    logger.info(f"Initiating credential creation for app under username {username}")
    client_id_seed = username + str(datetime.datetime.now())
    random.seed(client_id_seed)
    c_id = "".join(random.choices(string.ascii_letters + string.digits, k=20))
    c_secret_str = "".join(random.choices(string.ascii_letters + string.digits, k=30))
    ph = PasswordHasher()
    c_secret = ph.hash(c_secret_str)

    logger.info(f"Finalized credential creation for app under username {username}")
    return {
        "client_id": c_id,
        "client_secret": c_secret,
        "client_secret_str": c_secret_str,
    }


class CustomTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        username = request.META.get("HTTP_X_AUTHENTICATED_USERNAME")
        if not username:
            raise exceptions.AuthenticationFailed(
                "Header X-AUTHENTICATED-USERNAME expected user <str> found <None>"
            )
        try:
            user = User.objects.get(username=username)
            token = request.headers.get("Authorization").split(" ")[1]
            verified = verify_user_token(token, user)
            if verified["verified"]:
                return (user, None)
            else:
                raise exceptions.AuthenticationFailed(
                    f'Could not authenticate user. {verified["error"]}'
                )
        except Exception as e:
            if e.__class__ == User.DoesNotExist:
                raise exceptions.AuthenticationFailed("No such user")
            else:
                raise exceptions.AuthenticationFailed(f"Error : {e.__str__()}")


class CustomTokenScheme(OpenApiAuthenticationExtension):
    target_class = "utils.auth.CustomTokenAuthentication"
    name = "CustomTokenAuthentication"

    def get_security_definition(self, auto_schema):
        return {
            "type": "Bearer",
            "in": "header",
            "name": "Authorization",
            "description": "Token-based authentication with required prefix 'Bearer'",
        }
