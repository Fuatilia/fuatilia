import pytest
from apps.representatives.models import PositionChoices
from tests.factories import RepresentativeFactory

pytestmark = pytest.mark.django_db


def test_representative_factory(representative_factory):
    assert representative_factory is RepresentativeFactory


def test_representaive_created(representative_fixt):
    print("===================", representative_fixt)
    assert representative_fixt.position in PositionChoices.choices
    assert representative_fixt.full_name is not None
