from utils.testing_utils.generic_helpers import GenericTestCasesHelpers


class UserTestCasesHelpers(GenericTestCasesHelpers):
    def user_log_in(self, username, password):
        url = "/api/users/v1/login/user"
        data = {"username": username, "password": password}

        return self.client.post(url, data=data, format="json")

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

    def assign_role_to_user(self, username, token, id, role):
        url = "/api/users/v1/update/role"
        data = {"user_id": id, "role": role}

        return self.send_request(username, token, url, data, method="put")

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
