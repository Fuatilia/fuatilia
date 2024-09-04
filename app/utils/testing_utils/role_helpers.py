from typing import Dict
from utils.testing_utils.generic_helpers import GenericTestCasesHelpers


class RoleTestCasesHelpers(GenericTestCasesHelpers):
    # PERMISSIONS
    def create_permission(self, username, token, data=None):
        url = "/api/roles/v1/permission/create"

        if data is None:
            data = {
                "definition": "This permission is a test case",
                "permission_name": "can_do_tests",
            }
        return self.send_request(
            username, token, url, data=data, format="json", method="post"
        )

    def filter_permissions(self, username, token, param_dict=None):
        if param_dict is None or len(param_dict.keys()) < 1:
            fetch_user_url = "/api/roles/v1/permission/filter?items_per_page=10&page=1"
        else:
            filter_tring = self.generate_filter_string(param_dict)
            fetch_user_url = f"/api/roles/v1/permission/filter{filter_tring}"

        return self.send_request(username, token, fetch_user_url, method="get")

    def get_permission(self, username, token, id):
        url = f"/api/roles/v1/permission/{id}"

        return self.send_request(username, token, url, method="get")

    def delete_permission(self, username, token, id):
        url = f"/api/roles/v1/permission/{id}"

        return self.send_request(username, token, url, method="delete")

    # ROLES
    def create_role(self, username, token, data: Dict | None = None):
        url = "/api/roles/v1/create"
        if data is None:
            data = {
                "permissions": [
                    "add_user",
                    "change_user",
                    "view_user",
                    "delete_user",
                    "add_representative",
                    "change_representative",
                    "view_representative",
                    "delete_representative",
                    "add_bill",
                    "change_bill",
                    "view_bill",
                    "delete_bill",
                    "add_vote",
                    "change_vote",
                    "view_vote",
                    "delete_vote",
                    "add_group",
                    "change_group",
                    "view_group",
                    "delete_group",
                    "add_permission",
                    "change_permission",
                    "view_permission",
                    "delete_permission",
                ],
                "role_name": "admin",
                "action": "add",
            }

        return self.send_request(username, token, url, data, method="post")

    def update_permission_for_role(self, username, token, data: Dict | None = None):
        url = "/api/roles/v1/update-permissions"

        if not data:
            data = {
                "permissions": [
                    "add_bill_file",
                    "view_bill_file",
                ],
                "role_name": "admin",
                "action": "add",
            }

        return self.send_request(username, token, url, data, method="put")

    def filter_roles(self, username, token, param_dict=None):
        if param_dict is None or len(param_dict.keys()) < 1:
            fetch_user_url = "/api/roles/v1/filter?items_per_page=10&page=1"
        else:
            filter_tring = self.generate_filter_string(param_dict)
            fetch_user_url = f"/api/roles/v1/filter{filter_tring}"

        return self.send_request(username, token, fetch_user_url, method="get")

    def get_role(self, username, token, id):
        url = f"/api/roles/v1/{id}"

        return self.send_request(username, token, url, method="get")

    def delete_role(self, username, token, id):
        url = f"/api/roles/v1/{id}"

        return self.send_request(username, token, url, method="delete")
