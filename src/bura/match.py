"""A match: a series of hands, the score, and who deals next."""

import logging
from random import Random

from bura.actions import Action
from bura.dealing import Seat
from bura.game import Deal, Phase
from bura.rules import TrickResult

DEFAULT_TARGET: int = 3

logger: logging.Logger = logging.getLogger(__name__)


class Match:
    """Play hands until one player has won ``target`` of them.

    The winner of a hand scores one point. A hand won by a claim is followed
    by a hand dealt by the claimant; after a void hand the same player deals
    again. Use ``apply`` to play and ``next_deal`` to move on.
    """

    def __init__(
        self,
        first_dealer: Seat = Seat.ONE,
        target: int = DEFAULT_TARGET,
        rng: Random | None = None,
    ) -> None:
        """Start a match and deal its first hand."""

        if target < 1:
            raise ValueError("A match needs a target of at least 1 hand")
        self._rng: Random = rng if rng is not None else Random()
        self._target: int = target
        self._scores: list[int] = [0, 0]
        self._next_dealer: Seat = first_dealer
        self._deal_number: int = 1
        self._deal: Deal = Deal.start(first_dealer, self._rng)
        self._recorded: bool = False
        logger.info("Match started, first to %d", target)
        self._record_if_finished()

    @property
    def deal(self) -> Deal:
        """Return the hand being played (or just finished)."""

        return self._deal

    @property
    def deal_number(self) -> int:
        """Return the number of the current hand, starting at 1."""

        return self._deal_number

    @property
    def target(self) -> int:
        """Return how many hands win the match."""

        return self._target

    @property
    def scores(self) -> tuple[int, int]:
        """Return the hands won by seat ONE and seat TWO."""

        return self._scores[0], self._scores[1]

    @property
    def winner(self) -> Seat | None:
        """Return the player who won the match, or None while it goes on."""

        for seat in (Seat.ONE, Seat.TWO):
            if self._scores[seat] >= self._target:
                return seat
        return None

    @property
    def is_over(self) -> bool:
        """Return whether somebody has won the match."""

        return self.winner is not None

    def apply(self, seat: Seat, action: Action) -> TrickResult | None:
        """Play an action in the current hand and update the score if it ends."""

        result: TrickResult | None = self._deal.apply(seat, action)
        self._record_if_finished()
        return result

    def next_deal(self) -> Deal:
        """Deal the next hand. Allowed only after a hand ended, mid-match."""

        if self._deal.phase is not Phase.FINISHED:
            raise ValueError("The current hand is not finished")
        if self.is_over:
            raise ValueError("The match is over")
        self._deal_number += 1
        self._deal = Deal.start(self._next_dealer, self._rng)
        self._recorded = False
        logger.info("Hand %d dealt by %s", self._deal_number, self._next_dealer.name)
        self._record_if_finished()
        return self._deal

    def _record_if_finished(self) -> None:
        """Add the finished hand to the score, once, and pick the next dealer."""

        if self._deal.phase is not Phase.FINISHED or self._recorded:
            return
        self._recorded = True
        result = self._deal.result
        assert result is not None
        if result.winner is not None:
            self._scores[result.winner] += 1
        self._next_dealer = (
            result.claimant if result.claimant is not None else self._deal.dealer
        )
        logger.info("Score is now %s", self.scores)
