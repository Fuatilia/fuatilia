import logging
from rest_framework import status
from rest_framework.test import APITestCase
from utils.testing_utils.role_helpers import RoleTestCasesHelpers
from utils.testing_utils.user_helpers import UserTestCasesHelpers


class RoleTestCases(APITestCase, RoleTestCasesHelpers, UserTestCasesHelpers):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.create_superuser_bare()

    def test_user_can_create_role(self):
        login_response = self.user_log_in(
            self.superuser_username, self.superuser_password
        )

        response = self.create_role(
            self.superuser_username, login_response.data.get("access")
        )
        print(
            "================ >> ",
            self.test_user_can_create_role.__name__,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_filter_all_roles(self):
        login_response = self.user_log_in(
            self.superuser_username, self.superuser_password
        )

        response = self.filter_roles(
            self.superuser_username, login_response.data.get("access")
        )
        print(
            "================ >> ",
            self.test_user_can_filter_all_roles.__name__,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_role(self):
        login_response = self.user_log_in(
            self.superuser_username, self.superuser_password
        )
        response = self.create_role(
            self.superuser_username, login_response.data.get("access")
        )
        response = self.get_role(
            self.superuser_username,
            login_response.data.get("access"),
            response.data.get("data").get("id"),
        )
        print("================ >> ", self.test_user_can_get_role.__name__)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_role(self):
        login_response = self.user_log_in(
            self.superuser_username, self.superuser_password
        )
        response = self.create_role(
            self.superuser_username, login_response.data.get("access")
        )
        response = self.delete_role(
            self.superuser_username,
            login_response.data.get("access"),
            response.data.get("data").get("id"),
        )
        print("================ >> ", self.test_user_can_delete_role.__name__)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)
        return super().tearDown()


class PemissionTestCases(APITestCase, RoleTestCasesHelpers, UserTestCasesHelpers):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.create_superuser_bare()

    def test_user_can_create_permission(self):
        login_response = self.user_log_in(
            self.superuser_username, self.superuser_password
        )

        response = self.create_permission(
            self.superuser_username, login_response.data.get("access")
        )
        print(
            "================ >> ",
            self.test_user_can_create_permission.__name__,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_filter_all_permissions(self):
        login_response = self.user_log_in(
            self.superuser_username, self.superuser_password
        )
        response = self.filter_permissions(
            self.superuser_username, login_response.data.get("access")
        )
        print(
            "================ >> ",
            self.test_user_can_filter_all_permissions.__name__,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_permission(self):
        login_response = self.user_log_in(
            self.superuser_username, self.superuser_password
        )

        response = self.create_permission(
            self.superuser_username, login_response.data.get("access")
        )

        response = self.get_permission(
            self.superuser_username,
            login_response.data.get("access"),
            response.data.get("data").get("pk"),
        )
        print("================ >> ", self.test_user_can_get_permission.__name__)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_permission(self):
        login_response = self.user_log_in(
            self.superuser_username, self.superuser_password
        )
        response = self.create_permission(
            self.superuser_username, login_response.data.get("access")
        )
        response = self.delete_permission(
            self.superuser_username,
            login_response.data.get("access"),
            response.data.get("data").get("pk"),
        )
        print("================ >> ", self.test_user_can_delete_permission.__name__)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
