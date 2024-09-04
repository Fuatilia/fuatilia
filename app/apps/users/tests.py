import logging
from apps.users.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from utils.testing_utils.user_helpers import UserTestCasesHelpers
from utils.testing_utils.role_helpers import RoleTestCasesHelpers


class SuperUserTestCases(APITestCase, UserTestCasesHelpers, RoleTestCasesHelpers):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        test_superuser = User.objects.create_superuser(
            username=self.superuser_username, password=self.superuser_password
        )
        test_superuser.is_superuser = True
        test_superuser.is_staff = True
        test_superuser.password = self.superuser_password
        test_superuser.save()

    def test_superuser_can_log_in(self):
        response = self.user_log_in(self.superuser_username, self.superuser_password)
        print("================ >> ", self.test_superuser_can_log_in.__name__)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("access"))

    def test_superuser_can_create_admin_user(self):
        login_response = self.user_log_in(
            self.superuser_username, self.superuser_password
        )
        response = self.create_admin_user(
            self.superuser_username, login_response.data.get("access")
        )
        print(
            "================ >> ", self.test_superuser_can_create_admin_user.__name__
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_superuser_can_create_role(self):
        login_response = self.user_log_in(
            self.superuser_username, self.superuser_password
        )
        response = self.create_role(
            self.superuser_username, login_response.data.get("access")
        )
        print("================ >> ", self.test_superuser_can_create_role.__name__)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_superuser_can_assign_role_to_admin_user(self):
        login_response = self.user_log_in(
            self.superuser_username, self.superuser_password
        )

        user_response = self.create_admin_user(
            self.superuser_username, login_response.data.get("access")
        ).data
        role_response = self.create_role(
            self.superuser_username, login_response.data.get("access")
        ).data
        response = self.assign_role_to_user(
            self.superuser_username,
            login_response.data.get("access"),
            user_response.get("data").get("id"),
            role_response.get("data").get("name"),
        )
        print(
            "================ >> ",
            self.test_superuser_can_assign_role_to_admin_user.__name__,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)
        return super().tearDown()


class AdminUserTestCases(UserTestCasesHelpers):
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

    def test_admin_user_can_log_in(self):
        response = self.user_log_in(self.admin_username, self.admin_password)
        print("================ >> ", self.test_admin_user_can_log_in.__name__)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_can_create_regular_user(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)

        response = self.create_regular_user(
            self.admin_username, login_response.data.get("access")
        )
        print(
            "================ >> ",
            self.test_admin_user_can_create_regular_user.__name__,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_user_can_create_app_user(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)

        response = self.create_app_user(
            self.admin_username, login_response.data.get("access")
        )
        print(
            "================ >> ",
            self.test_admin_user_can_create_regular_user.__name__,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_user_can_filter_all_users(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)

        response = self.create_regular_user(
            self.admin_username, login_response.data.get("access")
        )

        response = self.filter_users(
            self.admin_username, login_response.data.get("access"), param_dict={}
        )
        print(
            "================ >> ", self.test_admin_user_can_filter_all_users.__name__
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_can_get_user(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)

        response = self.create_regular_user(
            self.admin_username, login_response.data.get("access")
        )

        response = self.get_user(
            self.admin_username,
            login_response.data.get("access"),
            response.data.get("data").get("id"),
        )
        print("================ >> ", self.test_admin_user_can_get_user.__name__)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_can_delete_user(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)

        response = self.create_regular_user(
            self.admin_username, login_response.data.get("access")
        )

        response = self.delete_user(
            self.admin_username,
            login_response.data.get("access"),
            response.data.get("data").get("id"),
        )
        print("================ >> ", self.test_admin_user_can_delete_user.__name__)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)
        return super().tearDown()
