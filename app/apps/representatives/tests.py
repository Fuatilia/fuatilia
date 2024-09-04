import logging
from rest_framework import status
from rest_framework.test import APITestCase
from utils.testing_utils.representative_helpers import RepresentativeTestCasesHelpers
from utils.testing_utils.user_helpers import UserTestCasesHelpers
from utils.testing_utils.role_helpers import RoleTestCasesHelpers


class RepresentativeTestCases(
    APITestCase,
    RoleTestCasesHelpers,
    RepresentativeTestCasesHelpers,
    UserTestCasesHelpers,
):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        superuser = self.create_superuser_bare()
        admin_user = self.create_admin_user_bare()
        login_response = self.user_log_in(superuser.username, self.superuser_password)

        role_creation_response = self.create_role(
            superuser.username, login_response.data.get("access")
        )
        self.assign_role_to_user(
            superuser.username,
            login_response.data.get("access"),
            admin_user.id,
            role_creation_response.data.get("data").get("name"),
        )

    def test_user_can_create_representative(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)

        response = self.create_representative(
            self.admin_username, login_response.data.get("access")
        )
        print(
            "================ >> ",
            self.test_user_can_create_representative.__name__,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_user_can_filter_all_representatives(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)

        response = self.create_representative(
            self.admin_username, login_response.data.get("access")
        )

        response = self.filter_representatives(
            self.admin_username, login_response.data.get("access"), param_dict={}
        )
        print(
            "================ >> ",
            self.test_admin_user_can_filter_all_representatives.__name__,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_can_get_representative(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)

        response = self.create_representative(
            self.admin_username, login_response.data.get("access")
        )

        response = self.get_representative(
            self.admin_username,
            login_response.data.get("access"),
            response.data.get("data").get("id"),
        )
        print(
            "================ >> ", self.test_admin_user_can_get_representative.__name__
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_representative(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)

        response = self.create_representative(
            self.admin_username, login_response.data.get("access")
        )
        response = self.delete_representative(
            self.admin_username,
            login_response.data.get("access"),
            response.data.get("data").get("id"),
        )
        print("================ >> ", self.test_user_can_delete_representative.__name__)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)
        return super().tearDown()
