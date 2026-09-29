"""Invariants of the Bura card model and pack."""

import unittest
from random import Random

from bura.cards import Card, Rank, Suit, trick_points
from bura.deck import Deck


class CardAndDeckTests(unittest.TestCase):
    """Check the complete pack and Bura's distinct rank/point rules."""

    def test_deck_has_36_unique_cards_worth_120_points(self) -> None:
        deck: Deck = Deck(Random(7))
        cards: list[Card] = [deck.draw() for _ in range(36)]

        self.assertEqual(len(set(cards)), 36)
        self.assertEqual(deck.remaining, 0)
        self.assertEqual(trick_points(cards), 120)
        with self.assertRaises(ValueError):
            deck.draw()

    def test_ten_beats_king_but_points_are_separate(self) -> None:
        self.assertGreater(Rank.TEN, Rank.KING)
        self.assertEqual(Card(Suit.HEARTS, Rank.TEN).points, 10)
        self.assertEqual(Card(Suit.HEARTS, Rank.KING).points, 4)
        self.assertEqual(Card(Suit.HEARTS, Rank.SIX).points, 0)

    def test_seeded_shuffle_can_be_reproduced(self) -> None:
        first_deck: Deck = Deck(Random(42))
        second_deck: Deck = Deck(Random(42))
        first: list[Card] = [first_deck.draw() for _ in range(36)]
        second: list[Card] = [second_deck.draw() for _ in range(36)]
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
