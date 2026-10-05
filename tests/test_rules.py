"""Behavior of single-card trick comparisons."""

import unittest

from bura.cards import Card, Rank, Suit
from bura.rules import beats


class SingleCardTrickTests(unittest.TestCase):
    """Check that rank, suit, and trump determine a winning response."""

    def test_higher_card_of_same_suit_wins(self) -> None:
        lead: Card = Card(Suit.HEARTS, Rank.KING)
        challenger: Card = Card(Suit.HEARTS, Rank.TEN)

        self.assertTrue(beats(challenger, lead, Suit.SPADES))
        self.assertFalse(beats(lead, challenger, Suit.SPADES))

    def test_trump_beats_even_an_ace_of_another_suit(self) -> None:
        lead: Card = Card(Suit.HEARTS, Rank.ACE)
        challenger: Card = Card(Suit.SPADES, Rank.SIX)

        self.assertTrue(beats(challenger, lead, Suit.SPADES))

    def test_non_trump_from_another_suit_cannot_win(self) -> None:
        lead: Card = Card(Suit.HEARTS, Rank.SIX)
        challenger: Card = Card(Suit.CLUBS, Rank.ACE)

        self.assertFalse(beats(challenger, lead, Suit.SPADES))

    def test_non_trump_cannot_beat_a_trump_lead(self) -> None:
        lead: Card = Card(Suit.SPADES, Rank.SIX)
        challenger: Card = Card(Suit.HEARTS, Rank.ACE)

        self.assertFalse(beats(challenger, lead, Suit.SPADES))

    def test_a_trump_needs_higher_rank_against_another_trump(self) -> None:
        lead: Card = Card(Suit.SPADES, Rank.TEN)
        challenger: Card = Card(Suit.SPADES, Rank.KING)

        self.assertFalse(beats(challenger, lead, Suit.SPADES))


if __name__ == "__main__":
    unittest.main()
