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

    def test_rank_order_is_bura_order(self) -> None:
        expected: list[Rank] = [
            Rank.SIX,
            Rank.SEVEN,
            Rank.EIGHT,
            Rank.NINE,
            Rank.JACK,
            Rank.QUEEN,
            Rank.KING,
            Rank.TEN,
            Rank.ACE,
        ]
        self.assertEqual(sorted(Rank), expected)

    def test_points_table(self) -> None:
        expected: dict[Rank, int] = {
            Rank.SIX: 0,
            Rank.SEVEN: 0,
            Rank.EIGHT: 0,
            Rank.NINE: 0,
            Rank.JACK: 2,
            Rank.QUEEN: 3,
            Rank.KING: 4,
            Rank.TEN: 10,
            Rank.ACE: 11,
        }
        self.assertEqual({rank: rank.points for rank in Rank}, expected)
    def test_card_rejects_raw_values(self) -> None:
        with self.assertRaises(TypeError):
            Card("hearts", Rank.TEN)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            Card(Suit.HEARTS, 7)  # type: ignore[arg-type]

    def test_card_labels(self) -> None:
        self.assertEqual(str(Card(Suit.HEARTS, Rank.TEN)), "10♥")
        self.assertEqual(str(Card(Suit.SPADES, Rank.ACE)), "A♠")
        self.assertEqual(str(Card(Suit.CLUBS, Rank.SIX)), "6♣")
        self.assertEqual(Rank.QUEEN.label, "Q")
        self.assertEqual(Suit.DIAMONDS.symbol, "♦")

if __name__ == "__main__":
    unittest.main()