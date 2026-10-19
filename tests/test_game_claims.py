"""Claiming 31 points: when it wins, when it loses, and who may claim."""

import unittest

from helpers import cs, scripted_deal

from bura.actions import Claim, Lead, Respond
from bura.dealing import Seat
from bura.game import Deal, DealResult, EndReason, IllegalActionError, Phase


def deal_where_two_has_25_points() -> Deal:
    """Seat TWO wins a trick of A, 10, K of hearts (25 points)."""

    deal: Deal = scripted_deal(
        ("6C", "7C", "8C"),
        ("AH", "10H", "KH"),
        ("QD", "JD", "6D", "9D", "7D", "8D"),
    )
    deal.apply(Seat.TWO, Lead(cs("AH", "10H", "KH")))
    deal.apply(Seat.ONE, Respond(cs("6C", "7C", "8C")))
    return deal


class ClaimTests(unittest.TestCase):
    """Check the outcome of a claim."""

    def test_a_claim_is_always_offered_to_the_player_to_act(self) -> None:
        deal: Deal = scripted_deal(("6C", "7C", "8C"), ("KH", "QD", "6D"), ())
        self.assertIn(Claim(), deal.legal_actions(Seat.TWO))
        self.assertNotIn(Claim(), deal.legal_actions(Seat.ONE))
        deal.apply(Seat.TWO, Lead(cs("KH")))
        self.assertIn(Claim(), deal.legal_actions(Seat.ONE))

    def test_exactly_31_points_wins(self) -> None:
        deal: Deal = scripted_deal(
            ("6C", "7C", "8C"),
            ("AH", "10H", "6D"),
            ("10D", "9D", "7D", "8D"),
        )
        deal.apply(Seat.TWO, Lead(cs("AH", "10H")))
        deal.apply(Seat.ONE, Respond(cs("6C", "7C")))
        deal.apply(Seat.TWO, Lead(cs("10D")))
        deal.apply(Seat.ONE, Respond(cs("8C")))
        deal.apply(Seat.TWO, Claim())

        self.assertIs(deal.phase, Phase.FINISHED)
        self.assertEqual(
            deal.result,
            DealResult(Seat.TWO, EndReason.CORRECT_CLAIM, Seat.TWO, 31),
        )

    def test_30_points_is_a_false_claim(self) -> None:
        deal: Deal = deal_where_two_has_25_points()
        deal.apply(Seat.TWO, Lead(cs("QD")))
        deal.apply(Seat.ONE, Respond(cs("JD")))
        deal.apply(Seat.TWO, Claim())

        self.assertEqual(
            deal.result,
            DealResult(Seat.ONE, EndReason.FALSE_CLAIM, Seat.TWO, 30),
        )

    def test_a_claim_with_few_points_loses(self) -> None:
        deal: Deal = deal_where_two_has_25_points()
        deal.apply(Seat.TWO, Claim())
        self.assertEqual(
            deal.result,
            DealResult(Seat.ONE, EndReason.FALSE_CLAIM, Seat.TWO, 25),
        )

    def test_the_responder_may_claim_before_answering(self) -> None:
        deal: Deal = scripted_deal(("6C", "7C", "8C"), ("KH", "QD", "6D"), ())
        deal.apply(Seat.TWO, Lead(cs("KH")))
        deal.apply(Seat.ONE, Claim())

        self.assertEqual(
            deal.result,
            DealResult(Seat.TWO, EndReason.FALSE_CLAIM, Seat.ONE, 0),
        )

    def test_only_the_player_to_act_may_claim(self) -> None:
        deal: Deal = scripted_deal(("6C", "7C", "8C"), ("KH", "QD", "6D"), ())
        with self.assertRaises(IllegalActionError):
            deal.apply(Seat.ONE, Claim())
        self.assertIsNone(deal.result)

    def test_nothing_can_be_played_after_a_claim(self) -> None:
        deal: Deal = scripted_deal(("6C", "7C", "8C"), ("KH", "QD", "6D"), ())
        deal.apply(Seat.TWO, Claim())
        with self.assertRaises(IllegalActionError):
            deal.apply(Seat.ONE, Lead(cs("6C")))
        self.assertEqual(deal.legal_actions(Seat.ONE), [])


if __name__ == "__main__":
    unittest.main()
