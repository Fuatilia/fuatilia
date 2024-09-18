import pytest
from tests.factories import BillFactory

pytestmark = pytest.mark.django_db


def test_bill_factory(bill_factory):
    assert bill_factory is BillFactory


def test_bill_creation(bill_fixt):
    assert bill_fixt.title is not None
