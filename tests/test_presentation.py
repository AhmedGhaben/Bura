"""Ordering, move lookup and wording used by the screen."""

import unittest

from helpers import cs, scripted_deal

from bura.actions import Lead, Respond
from bura.dealing import Seat
from bura.game import DealResult, EndReason
from bura.presentation import (
    find_action,
    result_lines,
    seat_name,
    selection_hint,
    sort_hand,
)
from bura.view import view_for


class PresentationTests(unittest.TestCase):
    """Check the pure helpers behind the screen."""

    def test_seat_names(self) -> None:
        self.assertEqual(seat_name(Seat.ONE), "Player 1")
        self.assertEqual(seat_name(Seat.TWO), "Player 2")

    def test_hands_are_sorted_by_suit_then_strongest_first(self) -> None:
        self.assertEqual(
            sort_hand(cs("6H", "AC", "10H", "KC")), list(cs("AC", "KC", "10H", "6H"))
        )

    def test_find_action_accepts_a_legal_lead_in_any_order(self) -> None:
        deal = scripted_deal(("6C", "7C", "8C"), ("KH", "QH", "6D"), ())
        self.assertEqual(
            find_action(deal, Seat.TWO, cs("QH", "KH")), Lead(cs("KH", "QH"))
        )

    def test_find_action_rejects_illegal_selections(self) -> None:
        deal = scripted_deal(("6C", "7C", "8C"), ("KH", "QH", "6D"), ())
        self.assertIsNone(find_action(deal, Seat.TWO, cs("KH", "6D")))
        self.assertIsNone(find_action(deal, Seat.TWO, ()))
        self.assertIsNone(find_action(deal, Seat.ONE, cs("6C")))

    def test_find_action_for_a_response(self) -> None:
        deal = scripted_deal(("6C", "7D", "8H"), ("KH", "QH", "6D"), ())
        deal.apply(Seat.TWO, Lead(cs("KH", "QH")))
        self.assertEqual(
            find_action(deal, Seat.ONE, cs("8H", "6C")), Respond(cs("6C", "8H"))
        )
        self.assertIsNone(find_action(deal, Seat.ONE, cs("6C")))

    def test_hints_name_the_number_of_cards(self) -> None:
        deal = scripted_deal(("6C", "7D", "8H"), ("KH", "QH", "6D"), ())
        self.assertIn("1 to 3", selection_hint(view_for(deal, Seat.TWO)))
        deal.apply(Seat.TWO, Lead(cs("KH", "QH")))
        self.assertIn("2 cards", selection_hint(view_for(deal, Seat.ONE)))

    def test_result_lines(self) -> None:
        false_claim = DealResult(Seat.ONE, EndReason.FALSE_CLAIM, Seat.TWO, 25)
        self.assertEqual(
            result_lines(false_claim),
            ["Player 2 claimed 31 but had only 25 points.", "Player 1 wins the hand."],
        )
        self.assertEqual(
            result_lines(DealResult(None, EndReason.EXHAUSTED))[1], "The hand is void."
        )
        self.assertIn("Bura", result_lines(DealResult(Seat.TWO, EndReason.BURA))[0])


if __name__ == "__main__":
    unittest.main()
