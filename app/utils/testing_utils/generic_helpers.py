from typing import Dict
from apps.users.models import User


class GenericTestCasesHelpers:
    superuser_username = "test_superuser"
    superuser_password = "test_password"
    admin_username = "test_user"
    admin_password = "test_password"

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

    def generate_filter_string(self, param_dict: Dict):
        filter_str = "?"

        for key in param_dict.keys():
            if filter_str[-1] == "?":
                filter_str = filter_str + f"{key}={param_dict[key]}"
            else:
                filter_str = filter_str + f"&{key}={param_dict[key]}"
