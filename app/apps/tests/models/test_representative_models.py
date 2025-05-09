import pytest
from app.utils.enum_utils import HouseChoices, PositionChoices, PositionClassChoices
from tests.factories import RepresentativeFactory

pytestmark = pytest.mark.django_db(databases=["default"])


def test_representative_factory(representative_factory):
    assert representative_factory is RepresentativeFactory


def test_representaive_created(representative_fixt):
    assert representative_fixt.position == PositionChoices.MP
    assert representative_fixt.position_class == PositionClassChoices.ELECTED
    assert representative_fixt.house == HouseChoices.NATIONAL
    assert representative_fixt.full_name is not None
