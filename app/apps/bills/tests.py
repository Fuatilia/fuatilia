import logging
from rest_framework import status
from rest_framework.test import APITestCase
from utils.testing_utils.representative_helpers import RepresentativeTestCasesHelpers
from utils.testing_utils.bill_helpers import BillTestCasesHelpers
from utils.testing_utils.user_helpers import UserTestCasesHelpers
from utils.testing_utils.role_helpers import RoleTestCasesHelpers


class BillTestCases(
    APITestCase,
    RoleTestCasesHelpers,
    BillTestCasesHelpers,
    UserTestCasesHelpers,
    RepresentativeTestCasesHelpers,
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

        # Initialize the sponsor and supporter representatives for bill functions/tests
        self.create_representative(
            superuser.username, login_response.data.get("access")
        )
        self.create_representative(
            superuser.username,
            login_response.data.get("access"),
            {
                "area_represented": "Test Area2",
                "full_name": "Mark Mende2",
                "house": "NATIONAL",
                "position": "MP",
                "position_type": "ELECTED",
                "gender": "M",
            },
        )

    def perform_bill_creation(self, login_response):
        rep_response = self.filter_representatives(
            self.admin_username, login_response.data.get("access")
        )

        self.sponsor_rep_id = rep_response.data.get("data")[0].get("id")
        self.supporter_rep_id = rep_response.data.get("data")[1].get("id")

        response = self.create_bill(
            self.admin_username,
            login_response.data.get("access"),
            {
                "topics_in_the_bill": "pesa",
                "title": "Finance Bill 2024",
                "status": "IN_PROGRESS",
                "sponsored_by": self.sponsor_rep_id,
                "supported_by": self.supporter_rep_id,
                "house": "NATIONAL",
            },
        )
        return response

    def test_user_can_create_bill(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)
        response = self.perform_bill_creation(login_response)
        print(
            "================ >> ",
            self.test_user_can_create_bill.__name__,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_user_can_filter_all_bills(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)

        response = self.perform_bill_creation(login_response)

        response = self.filter_bills(
            self.admin_username, login_response.data.get("access"), param_dict={}
        )
        print(
            "================ >> ", self.test_admin_user_can_filter_all_bills.__name__
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_can_get_bill(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)

        response = self.perform_bill_creation(login_response)

        response = self.get_bill(
            self.admin_username,
            login_response.data.get("access"),
            response.data.get("data").get("id"),
        )
        print("================ >> ", self.test_admin_user_can_get_bill.__name__)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_can_delete_bill(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)

        response = self.perform_bill_creation(login_response)

        response = self.delete_bill(
            self.admin_username,
            login_response.data.get("access"),
            response.data.get("data").get("id"),
        )
        print("================ >> ", self.test_admin_user_can_delete_bill.__name__)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)
        return super().tearDown()
