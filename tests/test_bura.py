"""Bura: a player who holds three trumps wins the hand at once."""

import unittest

from helpers import cs, scripted_deal

from bura.actions import Lead, Respond
from bura.dealing import Seat
from bura.game import Deal, DealResult, EndReason, Phase


class BuraTests(unittest.TestCase):
    """Check when three trumps end the hand."""

    def test_a_bura_in_the_opening_deal_wins_at_once(self) -> None:
        deal: Deal = scripted_deal(("6C", "7C", "8C"), ("6S", "7S", "8S"), ("9D",))

        self.assertIs(deal.phase, Phase.FINISHED)
        self.assertEqual(deal.result, DealResult(Seat.TWO, EndReason.BURA))
        self.assertIsNone(deal.to_act)
        self.assertEqual(deal.legal_actions(Seat.TWO), [])

    def test_the_non_leader_can_hold_the_bura(self) -> None:
        deal: Deal = scripted_deal(("6S", "7S", "8S"), ("KH", "QH", "6D"), ("9D",))
        self.assertEqual(deal.result, DealResult(Seat.ONE, EndReason.BURA))

    def test_if_both_hold_a_bura_the_leader_wins(self) -> None:
        deal: Deal = scripted_deal(("6S", "7S", "8S"), ("QS", "KS", "10S"), ("9D",))
        self.assertEqual(deal.result, DealResult(Seat.TWO, EndReason.BURA))

    def test_two_trumps_are_not_a_bura(self) -> None:
        deal: Deal = scripted_deal(("6S", "7S", "8C"), ("KH", "QH", "6D"), ("9D",))
        self.assertIsNone(deal.result)

    def test_a_bura_drawn_after_a_trick_ends_the_hand(self) -> None:
        deal: Deal = scripted_deal(
            ("6C", "7C", "8C"),
            ("KH", "6S", "7S"),
            ("8S", "9D", "7D", "6D"),
        )
        deal.apply(Seat.TWO, Lead(cs("KH")))
        deal.apply(Seat.ONE, Respond(cs("6C")))

        self.assertIs(deal.phase, Phase.FINISHED)
        self.assertEqual(deal.result, DealResult(Seat.TWO, EndReason.BURA))
        self.assertEqual(set(deal.hand(Seat.TWO)), set(cs("6S", "7S", "8S")))

    def test_a_bura_drawn_by_the_loser_wins_for_the_loser(self) -> None:
        deal: Deal = scripted_deal(
            ("6S", "7S", "8C"),
            ("KH", "QD", "6D"),
            ("9D", "8S", "7D", "9H"),
        )
        deal.apply(Seat.TWO, Lead(cs("KH")))
        deal.apply(Seat.ONE, Respond(cs("8C")))

        self.assertEqual(deal.result, DealResult(Seat.ONE, EndReason.BURA))


if __name__ == "__main__":
    unittest.main()
