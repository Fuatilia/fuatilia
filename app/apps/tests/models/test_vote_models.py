import pytest
from tests.factories import ConsensusVoteFactory, IndividualVoteFactory

pytestmark = pytest.mark.django_db


def test_individual_vote_factory(individual_vote_factory):
    assert individual_vote_factory is IndividualVoteFactory


def test_consensus_vote_factory(consensus_vote_factory):
    assert consensus_vote_factory is ConsensusVoteFactory


def test_individual_vote(individual_vote_fixt):
    assert individual_vote_fixt.vote in ["YES", "NO"]


def test_consensus_vote(consensus_vote_fixt):
    assert consensus_vote_fixt.vote_summary["YES"] == 100
    assert consensus_vote_fixt.vote_summary["NO"] == 20
    assert consensus_vote_fixt.vote_summary["ABSENT"] == 30
