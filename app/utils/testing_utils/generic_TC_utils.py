from typing import Dict
from rest_framework.test import APITestCase
from apps.users.models import User


class GenericTestCasesMethods(APITestCase):
    superuser_username = "test_superuser"
    superuser_password = "test_password"
    admin_username = "test_user"
    admin_password = "test_password"

    def user_log_in(self, username, password):
        url = "/api/users/v1/login/user"
        data = {"username": username, "password": password}

        return self.client.post(url, data=data, format="json")

    def send_request(
        self, username, token, url, data=None, method="post", format="json"
    ):
        headers = {
            "Authorization": f"Bearer {token}",
            "X-AUTHENTICATED-USERNAME": username,
        }
        if method == "post":
            response = self.client.post(url, data, format=format, headers=headers)
        elif method == "put":
            response = self.client.put(url, data, format=format, headers=headers)
        elif method == "get":
            response = self.client.get(url, headers=headers)
        elif method == "delete":
            response = self.client.delete(url, headers=headers)

        return response

    def create_superuser_bare(self):
        test_superuser = User.objects.create_user(
            username=self.superuser_username, password=self.superuser_password
        )
        test_superuser.is_superuser = True
        test_superuser.is_staff = True
        test_superuser.password = self.superuser_password
        test_superuser.save()
        return test_superuser

    def create_admin_user_bare(self):
        test_adminuser = User.objects.create_user(
            first_name="fname",
            last_name="lname",
            email="fnamelname@fuatilia.com",
            username=self.admin_username,
            phone_number="+254111111111",
            password=self.admin_password,
            role="ADMIN",
            parent_organization="fuatilia",
        )

        test_adminuser.password = self.admin_password
        test_adminuser.save()
        return test_adminuser

    def create_admin_user(self, username, token):
        url = "/api/users/v1/create/user"
        data = {
            "first_name": "fname",
            "last_name": "lname",
            "email": "fnamelname@fuatilia.com",
            "username": self.admin_username,
            "phone_number": "+254111111111",
            "password": self.admin_password,
            "role": "ADMIN",
            "parent_organization": "fuatilia",
        }

        return self.send_request(username, token, url, data, method="post")

    def create_regular_user(self, username, token):
        url = "/api/users/v1/create/user"
        data = {
            "first_name": "jane",
            "last_name": "doe",
            "email": "janedoe@fuatilia.com",
            "username": "janedoe",
            "phone_number": "+254111111111",
            "password": "password1234",
            "role": "STAFF",
            "parent_organization": "fuatilia",
        }

        return self.send_request(username, token, url, data, method="post")

    def create_app_user(self, username, token):
        url = "/api/users/v1/create/app"
        data = {
            "email": "janedoe@fuatilia.com",
            "username": "janedoe",
            "phone_number": "+254111111111",
            "parent_organization": "fuatilia",
            "user_type": "APP",
        }

        return self.send_request(username, token, url, data, method="post")

    def create_permission(self, username, token):
        url = "/api/roles/v1/permission/create"
        data = {
            "definition": "Test S3 bill files permission put",
            "permission_name": "add_bill_file",
        }

        return self.send_request(username, token, url, data, method="post")

    def create_admin_role(self, username, token):
        url = "/api/roles/v1/create"
        data = {
            "permissions": [
                "add_user",
                "change_user",
                "view_user",
                "delete_user",
                "add_representative",
                "change_representative",
                "view_representative",
                "delete_representative" "add_bill",
                "change_bill",
                "view_bill",
                "delete_user",
                "add_vote",
                "change_vote",
                "view_vote",
                "delete_vote",
                "add_group",
                "change_group",
                "view_group",
                "delete_group",
            ],
            "role_name": "admin",
            "action": "add",
        }

        return self.send_request(username, token, url, data, method="post")

    def assign_permission_to_role(self, username, token):
        url = "/api/roles/v1/update-permissions"
        data = {
            "permissions": [
                "add_vote",
                "change_vote",
                "view_vote",
                "delete_vote",
                "add_group",
                "change_group",
                "view_group",
                "delete_group",
                "add_bill_file",
            ],
            "role_name": "admin",
            "action": "add",
        }

        return self.send_request(username, token, url, data, method="put")

    def assign_role_to_user(self, username, token, id, role):
        url = "/api/users/v1/update/role"
        data = {"user_id": id, "role": role}

        return self.send_request(username, token, url, data, method="put")

    def generate_filter_string(self, param_dict: Dict):
        filter_str = "?"

        for key in param_dict.keys():
            if filter_str[-1] == "?":
                filter_str = filter_str + f"{key}={param_dict[key]}"
            else:
                filter_str = filter_str + f"&{key}={param_dict[key]}"

    def filter_users(self, username, token, param_dict=None):
        if param_dict is None or len(param_dict.keys()) < 1:
            fetch_user_url = "/api/users/v1/filter?items_per_page=10&page=1"
        else:
            filter_tring = self.generate_filter_string(param_dict)
            fetch_user_url = f"/api/users/v1/filter{filter_tring}"

        return self.send_request(username, token, fetch_user_url, method="get")

    def get_user(self, username, token, id):
        url = f"/api/users/v1/{id}"

        return self.send_request(username, token, url, method="get")

    def delete_user(self, username, token, id):
        url = f"/api/users/v1/{id}"

        return self.send_request(username, token, url, method="delete")
