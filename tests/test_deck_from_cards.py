"""Building a deck with the cards in a chosen order."""

import unittest

from bura.cards import Card, Rank, Suit
from bura.deck import Deck

ACE: Card = Card(Suit.HEARTS, Rank.ACE)
KING: Card = Card(Suit.HEARTS, Rank.KING)
QUEEN: Card = Card(Suit.HEARTS, Rank.QUEEN)


class DeckFromCardsTests(unittest.TestCase):
    """Check that a chosen order is respected."""

    def test_first_card_given_is_drawn_first(self) -> None:
        deck: Deck = Deck.from_cards([ACE, KING, QUEEN])

        self.assertEqual(deck.remaining, 3)
        self.assertEqual(deck.bottom_card, QUEEN)
        self.assertEqual([deck.draw() for _ in range(3)], [ACE, KING, QUEEN])

    def test_the_same_card_twice_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            Deck.from_cards([ACE, ACE])

    def test_an_empty_deck_is_allowed(self) -> None:
        deck: Deck = Deck.from_cards([])
        self.assertEqual(deck.remaining, 0)
        self.assertIsNone(deck.bottom_card)


if __name__ == "__main__":
    unittest.main()
