"""Playing tricks: leading, responding, winning, and drawing new cards."""

import unittest
from random import Random

from helpers import c, cs, scripted_deal

from bura.actions import Action, Claim, Lead, Respond
from bura.dealing import Seat
from bura.game import Deal, DealResult, EndReason, IllegalActionError, Phase
from bura.rules import TrickResult


class OpeningTests(unittest.TestCase):
    """Check the state of a freshly dealt hand."""

    def test_new_hand_waits_for_the_non_dealer_to_lead(self) -> None:
        deal: Deal = Deal.start(Seat.ONE, Random(1))

        self.assertIs(deal.phase, Phase.LEAD)
        self.assertIs(deal.to_act, Seat.TWO)
        self.assertEqual(deal.stock_size, 30)
        self.assertTrue(deal.trump_card_in_stock)
        self.assertEqual(deal.trump_suit, deal.trump_card.suit)
        self.assertIsNone(deal.result)
        self.assertIs(deal.dealer, Seat.ONE)

    def test_same_seed_gives_the_same_hand(self) -> None:
        first: Deal = Deal.start(Seat.TWO, Random(9))
        second: Deal = Deal.start(Seat.TWO, Random(9))
        self.assertEqual(first.hand(Seat.ONE), second.hand(Seat.ONE))
        self.assertEqual(first.trump_card, second.trump_card)


class LegalActionTests(unittest.TestCase):
    """Check which moves are offered."""

    def test_leads_are_single_cards_and_same_suit_groups(self) -> None:
        deal: Deal = scripted_deal(("6C", "7C", "8C"), ("KH", "QH", "6C"), ())
        actions: list[Action] = [
            action
            for action in deal.legal_actions(Seat.TWO)
            if not isinstance(action, Claim)
        ]

        self.assertEqual(len(actions), 4)
        self.assertIn(Lead(cs("KH", "QH")), actions)
        self.assertNotIn(Lead(cs("KH", "6C")), actions)

    def test_only_the_player_to_act_has_moves(self) -> None:
        deal: Deal = scripted_deal(("6C", "7C", "8C"), ("KH", "QH", "6D"), ())
        self.assertEqual(deal.legal_actions(Seat.ONE), [])

    def test_responses_may_use_any_cards_of_the_right_number(self) -> None:
        deal: Deal = scripted_deal(("6C", "7D", "8H"), ("KH", "QH", "6D"), ())
        deal.apply(Seat.TWO, Lead(cs("KH", "QH")))
        actions: list[Action] = [
            action
            for action in deal.legal_actions(Seat.ONE)
            if not isinstance(action, Claim)
        ]

        self.assertEqual(len(actions), 3)
        self.assertIn(Respond(cs("6C", "8H")), actions)


class TrickTests(unittest.TestCase):
    """Check who wins a trick and what happens next."""

    def test_leader_wins_when_the_answer_is_too_weak(self) -> None:
        deal: Deal = scripted_deal(
            ("6C", "7C", "8C"), ("KH", "QD", "6D"), ("9D", "8D", "7D")
        )
        deal.apply(Seat.TWO, Lead(cs("KH")))
        result: TrickResult | None = deal.apply(Seat.ONE, Respond(cs("6C")))

        assert result is not None
        self.assertFalse(result.responder_wins)
        self.assertIs(deal.leader, Seat.TWO)
        self.assertEqual(set(deal.captured(Seat.TWO)), set(cs("KH", "6C")))
        self.assertEqual(deal.captured(Seat.ONE), ())
        self.assertEqual(deal.last_trick, result)

    def test_responder_wins_with_a_higher_card_and_then_leads(self) -> None:
        deal: Deal = scripted_deal(
            ("AH", "7C", "8C"), ("KH", "QD", "6D"), ("9D", "8D", "7D")
        )
        deal.apply(Seat.TWO, Lead(cs("KH")))
        deal.apply(Seat.ONE, Respond(cs("AH")))

        self.assertIs(deal.leader, Seat.ONE)
        self.assertIs(deal.to_act, Seat.ONE)
        self.assertEqual(set(deal.captured(Seat.ONE)), set(cs("KH", "AH")))

    def test_trump_wins_the_trick(self) -> None:
        deal: Deal = scripted_deal(
            ("6S", "7C", "8C"), ("AH", "QD", "6D"), ("9D", "8D", "7D")
        )
        deal.apply(Seat.TWO, Lead(cs("AH")))
        deal.apply(Seat.ONE, Respond(cs("6S")))
        self.assertIs(deal.leader, Seat.ONE)

    def test_two_card_trick_needs_each_card_beaten(self) -> None:
        deal: Deal = scripted_deal(
            ("AH", "6H", "8C"), ("KH", "QH", "6D"), ("9D", "8D", "7D", "9C")
        )
        deal.apply(Seat.TWO, Lead(cs("KH", "QH")))
        deal.apply(Seat.ONE, Respond(cs("AH", "6H")))
        self.assertIs(deal.leader, Seat.TWO)


class DrawingTests(unittest.TestCase):
    """Check who draws what after a trick."""

    def test_the_trick_winner_draws_first_then_they_alternate(self) -> None:
        deal: Deal = scripted_deal(
            ("AH", "7C", "8C"), ("KH", "QD", "6D"), ("9D", "8D", "7D", "6C")
        )
        deal.apply(Seat.TWO, Lead(cs("KH")))
        deal.apply(Seat.ONE, Respond(cs("AH")))

        self.assertIn(c("9D"), deal.hand(Seat.ONE))
        self.assertIn(c("8D"), deal.hand(Seat.TWO))
        self.assertEqual(len(deal.hand(Seat.ONE)), 3)
        self.assertEqual(len(deal.hand(Seat.TWO)), 3)
        self.assertEqual(deal.stock_size, 3)

    def test_a_two_card_trick_draws_two_each(self) -> None:
        deal: Deal = scripted_deal(
            ("6C", "7C", "8C"), ("KH", "QH", "6D"), ("9D", "8D", "7D", "6H", "9H")
        )
        deal.apply(Seat.TWO, Lead(cs("KH", "QH")))
        deal.apply(Seat.ONE, Respond(cs("6C", "7C")))

        self.assertEqual(deal.hand(Seat.TWO), cs("6D", "9D", "7D"))
        self.assertEqual(deal.hand(Seat.ONE), cs("8C", "8D", "6H"))
        self.assertEqual(deal.stock_size, 2)

    def test_the_trump_card_is_drawn_last(self) -> None:
        deal: Deal = scripted_deal(
            ("6C", "7C", "8C"), ("KH", "QD", "6D"), ("9D",), trump_card="9S"
        )
        deal.apply(Seat.TWO, Lead(cs("KH")))
        deal.apply(Seat.ONE, Respond(cs("6C")))

        self.assertIn(c("9D"), deal.hand(Seat.TWO))
        self.assertIn(c("9S"), deal.hand(Seat.ONE))
        self.assertEqual(deal.stock_size, 0)
        self.assertFalse(deal.trump_card_in_stock)

    def test_leftover_stock_is_set_aside_when_it_cannot_go_round(self) -> None:
        deal: Deal = scripted_deal(
            ("6C", "7C", "8C"), ("KH", "QH", "6D"), ("9D",), trump_card="9S"
        )
        deal.apply(Seat.TWO, Lead(cs("KH", "QH")))
        deal.apply(Seat.ONE, Respond(cs("6C", "7C")))

        self.assertEqual(deal.stock_size, 0)
        self.assertEqual(set(deal.set_aside), set(cs("9D", "9S")))
        self.assertEqual(len(deal.hand(Seat.ONE)), 1)
        self.assertEqual(len(deal.hand(Seat.TWO)), 1)
        self.assertFalse(deal.trump_card_in_stock)
        self.assertIs(deal.phase, Phase.LEAD)


class EndOfHandTests(unittest.TestCase):
    """Check what happens when the cards run out."""

    def test_hand_ends_void_when_every_card_is_played(self) -> None:
        deal: Deal = scripted_deal(("6C",), ("KH",), ())
        deal.apply(Seat.TWO, Lead(cs("KH")))
        deal.apply(Seat.ONE, Respond(cs("6C")))

        self.assertIs(deal.phase, Phase.FINISHED)
        self.assertEqual(deal.result, DealResult(None, EndReason.EXHAUSTED))
        self.assertIsNone(deal.to_act)
        self.assertEqual(deal.legal_actions(Seat.ONE), [])
        self.assertEqual(deal.legal_actions(Seat.TWO), [])

    def test_nothing_can_be_played_after_the_hand_ends(self) -> None:
        deal: Deal = scripted_deal(("6C",), ("KH",), ())
        deal.apply(Seat.TWO, Lead(cs("KH")))
        deal.apply(Seat.ONE, Respond(cs("6C")))
        with self.assertRaises(IllegalActionError):
            deal.apply(Seat.TWO, Lead(cs("KH")))


class IllegalActionTests(unittest.TestCase):
    """Check that mistakes are refused and change nothing."""

    def setUp(self) -> None:
        self.deal: Deal = scripted_deal(
            ("6C", "7C", "8C"), ("KH", "QH", "6D"), ("9D", "8D", "7D")
        )

    def test_acting_out_of_turn(self) -> None:
        with self.assertRaises(IllegalActionError):
            self.deal.apply(Seat.ONE, Lead(cs("6C")))

    def test_playing_a_card_you_do_not_hold(self) -> None:
        with self.assertRaises(IllegalActionError):
            self.deal.apply(Seat.TWO, Lead(cs("AH")))
        self.assertEqual(self.deal.hand(Seat.TWO), cs("KH", "QH", "6D"))

    def test_a_lead_of_mixed_suits(self) -> None:
        with self.assertRaises(IllegalActionError):
            self.deal.apply(Seat.TWO, Lead(cs("KH", "6D")))
        self.assertIs(self.deal.phase, Phase.LEAD)

    def test_the_same_card_twice(self) -> None:
        with self.assertRaises(IllegalActionError):
            self.deal.apply(Seat.TWO, Lead(cs("KH", "KH")))

    def test_responding_when_a_lead_is_needed(self) -> None:
        with self.assertRaises(IllegalActionError):
            self.deal.apply(Seat.TWO, Respond(cs("KH")))

    def test_leading_when_an_answer_is_needed(self) -> None:
        self.deal.apply(Seat.TWO, Lead(cs("KH")))
        with self.assertRaises(IllegalActionError):
            self.deal.apply(Seat.ONE, Lead(cs("6C")))

    def test_answering_with_the_wrong_number_of_cards(self) -> None:
        self.deal.apply(Seat.TWO, Lead(cs("KH", "QH")))
        with self.assertRaises(IllegalActionError):
            self.deal.apply(Seat.ONE, Respond(cs("6C")))
        self.assertEqual(self.deal.hand(Seat.ONE), cs("6C", "7C", "8C"))


if __name__ == "__main__":
    unittest.main()
