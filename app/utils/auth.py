import functools
import os
from typing import List
import jwt
import random
import string
import logging
import datetime
from apps.users.models import User
from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth.hashers import Argon2PasswordHasher
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object

logger = logging.getLogger("app_logger")

HASH_SECRET_STR = os.environ.get("HASH_SECRET_STR")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
TOKEN_DELTA = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def get_tokens_for_user(user: User, scope: str = ""):
    iat = datetime.datetime.now()
    exp_time = iat + datetime.timedelta(minutes=TOKEN_DELTA)
    exp_epoch = int(exp_time.timestamp())
    data = {
        "scope": scope,
        "username": user.username,
        "id": str(user.id),
        "role": list(user.groups.values_list("name", flat=True)),
        "user_type": user.user_type,
        "organisation": user.parent_organization,
        "exp": exp_epoch,
        "iat": int(iat.timestamp()),
    }

    token = jwt.encode(data, HASH_SECRET_STR, algorithm=JWT_ALGORITHM)
    return {"access": str(token), "exp": exp_epoch}


def verify_user_token(token: str, user: User):
    logger.info(f"Verifying user token for {user.id}")
    try:
        decoded_data = jwt.decode(token, HASH_SECRET_STR, algorithms=[JWT_ALGORITHM])
    except Exception as e:
        logger.exception(e)
        logger.error(f"Failed to verify user token for {user.id}")
        return {"verified": False, "error": e.__str__()}

    if decoded_data.get("username") != user.username:
        logger.error(f"Failed to verify user token for {user.id}")
        return {"verified": False, "error": "Invalid user token"}

    if not user.is_active and "email_verification" in decoded_data.get("scope"):
        # Allow verification of email tokens
        logger.info(f"Verified user token for {user.id}")
        return {"verified": True, "scope": "email_verification"}

    if "user_credential_reset" in decoded_data.get("scope"):
        # Allow verification of credential reset tokens
        logger.info(f"Verified user token for {user.id}")
        return {"verified": True, "scope": "user_credential_reset"}

    logger.error(f"Failed to verify user token for {user.id}")
    return {"verified": False, "error": "Unverified account/email/user"}


def create_client_id_and_secret(username: str):
    logger.info(f"Initiating credential creation for app under username {username}")
    client_id_seed = username + str(datetime.datetime.now())
    random.seed(client_id_seed)
    c_id = "".join(random.choices(string.ascii_letters + string.digits, k=20))
    c_secret_str = "".join(random.choices(string.ascii_letters + string.digits, k=30))
    ph = Argon2PasswordHasher()
    CLIENT_ID_SECRET_SALT = os.environ.get("CLIENT_ID_SECRET_SALT")

    c_secret = ph.encode(c_secret_str, CLIENT_ID_SECRET_SALT)

    logger.info(f"Finalized credential creation for app under username {username}")
    return {
        "client_id": c_id,
        "client_secret": c_secret,
        "client_secret_str": c_secret_str,
    }


def has_expected_permissions(permission_list: List[str]):
    def decorator_expected_permissions(func):
        @functools.wraps(func)
        def wrapper_expected_permissions(*args, **kwargs):
            user: User = args[1].user
            if not user.is_superuser:
                # Whatever is going on after this if-check does not look like I should have done it
                # Need to find a way to make it quicker
                try:
                    user = User.objects.get(username=user.username)
                except Exception as user_fetch_exp:
                    # In the event of something like AnonymousUser
                    logger.error(
                        f"Unable to authenticate user << {user} >> error {user_fetch_exp}"
                    )
                    raise exceptions.AuthenticationFailed(
                        "Unable to authenticate user. Token is invalid or missing"
                    )
                user_groups = list(user.groups.all())

                # Current assumption is that a user will belong to one role
                if len(user_groups) < 1:
                    user_permissions_list = []
                else:
                    user_permissions = user_groups[0].permissions.all()
                    user_permissions_list = [
                        permission.codename for permission in user_permissions
                    ]

                for permission in permission_list:
                    # If permissions are assigned individualy
                    if permission not in user_permissions_list:
                        raise exceptions.AuthenticationFailed(
                            f"User does not have permission --> {permission}"
                        )

            return func(*args, **kwargs)

        return wrapper_expected_permissions

    return decorator_expected_permissions


class CustomTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        username = request.META.get("HTTP_X_AUTHENTICATED_USERNAME")
        if not username:
            raise exceptions.AuthenticationFailed(
                "Header X-AUTHENTICATED-USERNAME expected user <str> found <None>"
            )
        try:
            user = User.objects.get(username=username)
            token = request.headers.get("Authorization")
            if not token:
                raise exceptions.AuthenticationFailed(
                    "Expected <str> in Authorization found <none>"
                )

            token = token.split(" ")[1]
            verified = verify_user_token(token, user)
            if verified["verified"]:
                return (user, None)
            else:
                raise exceptions.AuthenticationFailed(
                    f'Could not authenticate user. {verified["error"]}'
                )

        except Exception as e:
            if e.__class__ == User.DoesNotExist:
                raise exceptions.AuthenticationFailed("Could not authenticate user.")
            else:
                raise exceptions.AuthenticationFailed(f"Error : {e.__str__()}")


class CustomTokenScheme(OpenApiAuthenticationExtension):
    target_class = "utils.auth.CustomTokenAuthentication"
    name = "CustomTokenAuthentication"

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name="Authorization",
            token_prefix="Bearer ",
        )
