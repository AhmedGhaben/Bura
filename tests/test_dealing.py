"""Behavior of the deck's bottom card and the opening deal."""

import unittest
from random import Random

from bura.cards import Card, Rank, Suit
from bura.dealing import HAND_SIZE, DealSetup, Seat, deal
from bura.deck import DECK_SIZE, Deck


class DeckBottomTests(unittest.TestCase):
    """Check that a card put on the bottom is drawn last."""

    def test_bottom_card_is_drawn_last(self) -> None:
        deck: Deck = Deck(Random(1))
        card: Card = deck.draw()
        deck.put_on_bottom(card)

        self.assertEqual(deck.bottom_card, card)
        drawn: list[Card] = [deck.draw() for _ in range(DECK_SIZE)]
        self.assertEqual(drawn[-1], card)
        self.assertIsNone(deck.bottom_card)

    def test_card_already_in_deck_cannot_be_added(self) -> None:
        deck: Deck = Deck(Random(1))
        with self.assertRaises(ValueError):
            deck.put_on_bottom(Card(Suit.HEARTS, Rank.ACE))


class SeatTests(unittest.TestCase):
    """Check the two seats at the table."""

    def test_other_seat(self) -> None:
        self.assertIs(Seat.ONE.other, Seat.TWO)
        self.assertIs(Seat.TWO.other, Seat.ONE)


class DealTests(unittest.TestCase):
    """Check dealing order, the trump card, and card conservation."""

    def test_each_player_gets_three_and_the_stock_has_thirty(self) -> None:
        deck: Deck = Deck(Random(3))
        setup: DealSetup = deal(deck, Seat.ONE)

        self.assertEqual(len(setup.hand(Seat.ONE)), HAND_SIZE)
        self.assertEqual(len(setup.hand(Seat.TWO)), HAND_SIZE)
        self.assertEqual(deck.remaining, 30)

    def test_cards_are_dealt_one_at_a_time_non_dealer_first(self) -> None:
        reference: Deck = Deck(Random(5))
        order: list[Card] = [reference.draw() for _ in range(2 * HAND_SIZE + 1)]

        setup: DealSetup = deal(Deck(Random(5)), Seat.ONE)

        self.assertEqual(setup.hand(Seat.TWO), (order[0], order[2], order[4]))
        self.assertEqual(setup.hand(Seat.ONE), (order[1], order[3], order[5]))
        self.assertEqual(setup.trump_card, order[6])

    def test_trump_card_is_at_the_bottom_and_drawn_last(self) -> None:
        deck: Deck = Deck(Random(8))
        setup: DealSetup = deal(deck, Seat.TWO)

        self.assertEqual(deck.bottom_card, setup.trump_card)
        self.assertEqual(setup.trump_suit, setup.trump_card.suit)
        stock: list[Card] = [deck.draw() for _ in range(deck.remaining)]
        self.assertEqual(stock[-1], setup.trump_card)

    def test_all_36_cards_are_accounted_for(self) -> None:
        deck: Deck = Deck(Random(13))
        setup: DealSetup = deal(deck, Seat.ONE)
        stock: list[Card] = [deck.draw() for _ in range(deck.remaining)]

        everything: list[Card] = [
            *setup.hand(Seat.ONE),
            *setup.hand(Seat.TWO),
            *stock,
        ]
        self.assertEqual(len(everything), DECK_SIZE)
        self.assertEqual(len(set(everything)), DECK_SIZE)

    def test_non_dealer_leads_first(self) -> None:
        self.assertIs(deal(Deck(Random(2)), Seat.ONE).first_leader, Seat.TWO)
        self.assertIs(deal(Deck(Random(2)), Seat.TWO).first_leader, Seat.ONE)

    def test_same_seed_gives_same_deal(self) -> None:
        first: DealSetup = deal(Deck(Random(21)), Seat.ONE)
        second: DealSetup = deal(Deck(Random(21)), Seat.ONE)
        self.assertEqual(first, second)

    def test_deal_needs_a_full_deck(self) -> None:
        deck: Deck = Deck(Random(4))
        deck.draw()
        with self.assertRaises(ValueError):
            deal(deck, Seat.ONE)


if __name__ == "__main__":
    unittest.main()
