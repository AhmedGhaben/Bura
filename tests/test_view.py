"""What each player's view reveals and hides."""

import unittest

from helpers import cs, scripted_deal

from bura.actions import Lead, Respond
from bura.dealing import Seat
from bura.game import Deal, Phase
from bura.view import PlayerView, view_for


class ViewTests(unittest.TestCase):
    """Check the contents of a view."""

    def setUp(self) -> None:
        self.deal: Deal = scripted_deal(
            ("6C", "7C", "8C"), ("KH", "QH", "6D"), ("9D", "8D", "7D", "6H", "9H")
        )

    def test_a_view_shows_own_hand_and_only_counts_for_the_rest(self) -> None:
        view: PlayerView = view_for(self.deal, Seat.ONE)

        self.assertEqual(view.hand, cs("6C", "7C", "8C"))
        self.assertEqual(view.opponent_hand_size, 3)
        self.assertEqual(view.stock_size, 6)
        self.assertTrue(view.trump_card_in_stock)
        self.assertEqual(view.trump_card, self.deal.trump_card)
        self.assertEqual(view.table_lead, ())
        self.assertFalse(view.is_my_turn)
        self.assertTrue(view_for(self.deal, Seat.TWO).is_my_turn)

    def test_the_opponents_cards_are_not_in_the_view(self) -> None:
        view: PlayerView = view_for(self.deal, Seat.ONE)
        opponent_cards: set[object] = set(cs("KH", "QH", "6D"))
        self.assertFalse(opponent_cards & set(view.hand))

    def test_the_lead_on_the_table_is_visible_to_the_responder(self) -> None:
        self.deal.apply(Seat.TWO, Lead(cs("KH", "QH")))
        view: PlayerView = view_for(self.deal, Seat.ONE)

        self.assertEqual(view.table_lead, cs("KH", "QH"))
        self.assertIs(view.phase, Phase.RESPOND)
        self.assertEqual(view.opponent_hand_size, 1)
        self.assertTrue(view.is_my_turn)

    def test_captured_cards_are_counts_not_cards(self) -> None:
        self.deal.apply(Seat.TWO, Lead(cs("KH", "QH")))
        self.deal.apply(Seat.ONE, Respond(cs("6C", "7C")))

        winner: PlayerView = view_for(self.deal, Seat.TWO)
        loser: PlayerView = view_for(self.deal, Seat.ONE)
        self.assertEqual(winner.own_captured_count, 4)
        self.assertEqual(winner.opponent_captured_count, 0)
        self.assertEqual(loser.own_captured_count, 0)
        self.assertEqual(loser.opponent_captured_count, 4)
        self.assertIsNotNone(winner.last_trick)

    def test_the_trump_card_stops_being_in_the_stock_once_drawn(self) -> None:
        deal: Deal = scripted_deal(
            ("6C", "7C", "8C"), ("KH", "QD", "6D"), ("9D",)
        )
        deal.apply(Seat.TWO, Lead(cs("KH")))
        deal.apply(Seat.ONE, Respond(cs("6C")))
        view: PlayerView = view_for(deal, Seat.ONE)

        self.assertFalse(view.trump_card_in_stock)
        self.assertIn(view.trump_card, view.hand)


if __name__ == "__main__":
    unittest.main()
