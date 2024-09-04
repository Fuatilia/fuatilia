import logging
import random
from rest_framework import status
from rest_framework.test import APITestCase
from apps.votes.models import VoteTypeChoices
from utils.testing_utils.role_helpers import RoleTestCasesHelpers
from utils.testing_utils.vote_helpers import VoteTestCasesHelpers
from utils.testing_utils.user_helpers import UserTestCasesHelpers
from utils.testing_utils.bill_helpers import BillTestCasesHelpers
from utils.testing_utils.representative_helpers import RepresentativeTestCasesHelpers


class VoteTestCases(
    APITestCase,
    RoleTestCasesHelpers,
    VoteTestCasesHelpers,
    UserTestCasesHelpers,
    BillTestCasesHelpers,
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

    def perform_vote_creation(self, login_response, vote_type: str | None = None):
        rep_response = self.filter_representatives(
            self.admin_username, login_response.data.get("access")
        )
        sponsor_rep_id = rep_response.data.get("data")[0].get("id")
        supporter_rep_id = rep_response.data.get("data")[1].get("id")

        bill_response = self.create_bill(
            self.admin_username,
            login_response.data.get("access"),
            {
                "topics_in_the_bill": "pesa",
                "title": f"Finance Bill {random.randint(2020, 2030)}",
                "status": "IN_PROGRESS",
                "sponsored_by": sponsor_rep_id,
                "supported_by": supporter_rep_id,
                "house": "NATIONAL",
            },
        )

        if vote_type == VoteTypeChoices.CONCENSUS:
            # Create consensus vote type
            response = self.create_vote(
                self.admin_username,
                login_response.data.get("access"),
                {
                    "bill_id": bill_response.data.get("data").get("id"),
                    "vote_type": VoteTypeChoices.CONCENSUS,
                    "vote_summary": {"YES": 100, "NO": 20, "ABSENT": 30},
                    "house": "NATIONAL",
                },
            )

        else:
            # Create individual vote type
            response = self.create_vote(
                self.admin_username,
                login_response.data.get("access"),
                {
                    "vote": "YES",
                    "bill_id": bill_response.data.get("data").get("id"),
                    "representative_id": sponsor_rep_id,
                    "vote_type": VoteTypeChoices.INDIVIDUAL,
                    "house": "NATIONAL",
                },
            )

        return response

    def test_user_can_create_individual_type_vote(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)
        response = self.perform_vote_creation(login_response)
        print(
            "================ >> ",
            self.test_user_can_create_individual_type_vote.__name__,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_create_consensus_type_vote(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)
        response = self.perform_vote_creation(
            login_response, vote_type=VoteTypeChoices.CONCENSUS
        )
        print(
            "================ >> ",
            self.test_user_can_create_consensus_type_vote.__name__,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_user_can_filter_all_votes(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)
        self.perform_vote_creation(login_response, vote_type=VoteTypeChoices.CONCENSUS)
        self.perform_vote_creation(login_response)
        response = self.filter_votes(
            self.admin_username, login_response.data.get("access"), param_dict={}
        )
        print(
            "================ >> ", self.test_admin_user_can_filter_all_votes.__name__
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_can_get_vote(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)
        vote_creation_response = self.perform_vote_creation(login_response)
        response = self.get_vote(
            self.admin_username,
            login_response.data.get("access"),
            vote_creation_response.data.get("data").get("id"),
        )
        print("================ >> ", self.test_admin_user_can_get_vote.__name__)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_can_delete_vote(self):
        login_response = self.user_log_in(self.admin_username, self.admin_password)
        vote_creation_response = self.perform_vote_creation(login_response)

        response = self.delete_vote(
            self.admin_username,
            login_response.data.get("access"),
            vote_creation_response.data.get("data").get("id"),
        )
        print("================ >> ", self.test_admin_user_can_delete_vote.__name__)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)
        return super().tearDown()
