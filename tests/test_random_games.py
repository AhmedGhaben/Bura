"""Whole hands played with random legal moves must always stay consistent."""

import unittest
from random import Random

from bura.actions import Action, Claim
from bura.cards import Card
from bura.dealing import Seat
from bura.deck import DECK_SIZE
from bura.game import Deal, EndReason, Phase
from bura.view import PlayerView, view_for

GAMES: int = 300
MOST_ACTIONS_IN_A_HAND: int = 40


def count_all_cards(deal: Deal) -> int:
    """Count every card: hands, stock, captured, set aside, and on the table."""

    return (
        len(deal.hand(Seat.ONE))
        + len(deal.hand(Seat.TWO))
        + deal.stock_size
        + len(deal.captured(Seat.ONE))
        + len(deal.captured(Seat.TWO))
        + len(deal.set_aside)
        + len(deal.table_lead)
    )


def cards_outside_the_stock(deal: Deal) -> list[Card]:
    """List every card we can see directly (everything but the stock)."""

    return [
        *deal.hand(Seat.ONE),
        *deal.hand(Seat.TWO),
        *deal.captured(Seat.ONE),
        *deal.captured(Seat.TWO),
        *deal.set_aside,
        *deal.table_lead,
    ]


def play_random_hand(seed: int) -> Deal:
    """Play a hand with random non-claim moves, checking it at every step."""

    rng: Random = Random(seed)
    deal: Deal = Deal.start(Seat(seed % 2), rng)

    for _ in range(MOST_ACTIONS_IN_A_HAND):
        seat: Seat | None = deal.to_act
        if seat is None:
            break
        moves: list[Action] = [
            move for move in deal.legal_actions(seat) if not isinstance(move, Claim)
        ]
        deal.apply(seat, rng.choice(moves))
        assert count_all_cards(deal) == DECK_SIZE
        outside: list[Card] = cards_outside_the_stock(deal)
        assert len(set(outside)) == len(outside)
        check_views(deal)
    return deal


def check_views(deal: Deal) -> None:
    """Make sure neither player's view leaks the other player's hand."""

    for seat in (Seat.ONE, Seat.TWO):
        view: PlayerView = view_for(deal, seat)
        opponent_hand: set[Card] = set(deal.hand(seat.other))
        seen: set[Card] = set(view.hand) | set(view.table_lead)
        if view.last_trick is not None:
            seen |= set(view.last_trick.cards)
        assert not (opponent_hand & seen)
        assert view.opponent_hand_size == len(opponent_hand)


class RandomGameTests(unittest.TestCase):
    """Play many seeded hands from start to finish."""

    def test_every_random_hand_ends_and_keeps_all_36_cards(self) -> None:
        for seed in range(GAMES):
            deal: Deal = play_random_hand(seed)

            self.assertIs(deal.phase, Phase.FINISHED, f"seed {seed}")
            assert deal.result is not None
            self.assertEqual(count_all_cards(deal), DECK_SIZE)
            if deal.result.reason is EndReason.BURA:
                self.assertIsNotNone(deal.result.winner)
            else:
                self.assertIs(deal.result.reason, EndReason.EXHAUSTED)
                self.assertIsNone(deal.result.winner)
                self.assertEqual(deal.stock_size, 0)
                self.assertEqual(len(deal.hand(Seat.ONE)), 0)
                self.assertEqual(len(deal.hand(Seat.TWO)), 0)

    def test_some_random_hands_set_cards_aside(self) -> None:
        aside: list[int] = [
            len(play_random_hand(seed).set_aside) for seed in range(GAMES)
        ]
        self.assertTrue(any(aside))
        self.assertTrue(all(count % 2 == 0 for count in aside))

    def test_the_same_seed_plays_the_same_hand(self) -> None:
        first: Deal = play_random_hand(5)
        second: Deal = play_random_hand(5)
        self.assertEqual(first.captured(Seat.ONE), second.captured(Seat.ONE))
        self.assertEqual(first.set_aside, second.set_aside)


if __name__ == "__main__":
    unittest.main()
