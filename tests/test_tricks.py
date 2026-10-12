"""Behavior of multi-card leads and trick resolution."""

import unittest

from bura.cards import Card, Rank, Suit
from bura.rules import beating_pairs, is_valid_lead, resolve_trick

TRUMP: Suit = Suit.SPADES


def hearts(rank: Rank) -> Card:
    """Return the heart of the given rank."""

    return Card(Suit.HEARTS, rank)


def spades(rank: Rank) -> Card:
    """Return the spade (trump in these tests) of the given rank."""

    return Card(Suit.SPADES, rank)


def clubs(rank: Rank) -> Card:
    """Return the club of the given rank."""

    return Card(Suit.CLUBS, rank)


class LeadTests(unittest.TestCase):
    """Check which groups of cards may be led."""

    def test_one_to_three_cards_of_one_suit_are_valid(self) -> None:
        self.assertTrue(is_valid_lead([hearts(Rank.SIX)]))
        self.assertTrue(is_valid_lead([hearts(Rank.SIX), hearts(Rank.ACE)]))
        self.assertTrue(
            is_valid_lead([spades(Rank.SIX), spades(Rank.TEN), spades(Rank.ACE)])
        )

    def test_invalid_leads_are_rejected(self) -> None:
        self.assertFalse(is_valid_lead([]))
        self.assertFalse(is_valid_lead([hearts(Rank.KING), clubs(Rank.KING)]))
        self.assertFalse(
            is_valid_lead(
                [
                    hearts(Rank.SIX),
                    hearts(Rank.SEVEN),
                    hearts(Rank.EIGHT),
                    hearts(Rank.NINE),
                ]
            )
        )
        self.assertFalse(is_valid_lead([hearts(Rank.KING), hearts(Rank.KING)]))


class TrickResolutionTests(unittest.TestCase):
    """Check that every led card must be beaten by its own response card."""

    def test_response_order_does_not_matter(self) -> None:
        lead: list[Card] = [hearts(Rank.TEN), hearts(Rank.SEVEN)]
        for response in (
            [hearts(Rank.EIGHT), hearts(Rank.ACE)],
            [hearts(Rank.ACE), hearts(Rank.EIGHT)],
        ):
            result = resolve_trick(lead, response, TRUMP)
            self.assertTrue(result.responder_wins)
            self.assertIn((hearts(Rank.TEN), hearts(Rank.ACE)), result.pairs)
            self.assertIn((hearts(Rank.SEVEN), hearts(Rank.EIGHT)), result.pairs)

    def test_one_card_cannot_beat_two(self) -> None:
        result = resolve_trick(
            [hearts(Rank.KING), hearts(Rank.QUEEN)],
            [hearts(Rank.ACE), hearts(Rank.SIX)],
            TRUMP,
        )
        self.assertFalse(result.responder_wins)
        self.assertEqual(result.pairs, ())

    def test_trumps_beat_any_non_trump_lead(self) -> None:
        result = resolve_trick(
            [hearts(Rank.ACE), hearts(Rank.TEN), hearts(Rank.KING)],
            [spades(Rank.SIX), spades(Rank.SEVEN), spades(Rank.EIGHT)],
            TRUMP,
        )
        self.assertTrue(result.responder_wins)

    def test_non_trump_cannot_beat_trump_lead(self) -> None:
        result = resolve_trick(
            [spades(Rank.KING), spades(Rank.QUEEN)],
            [spades(Rank.ACE), hearts(Rank.ACE)],
            TRUMP,
        )
        self.assertFalse(result.responder_wins)

    def test_partial_beat_loses_and_all_cards_go_to_the_winner(self) -> None:
        result = resolve_trick(
            [hearts(Rank.SIX), hearts(Rank.SEVEN), hearts(Rank.EIGHT)],
            [hearts(Rank.ACE), hearts(Rank.TEN), clubs(Rank.SIX)],
            TRUMP,
        )
        self.assertFalse(result.responder_wins)
        self.assertEqual(len(result.cards), 6)

    def test_points_count_all_six_cards(self) -> None:
        result = resolve_trick(
            [hearts(Rank.KING), hearts(Rank.QUEEN), hearts(Rank.JACK)],
            [hearts(Rank.ACE), hearts(Rank.TEN), clubs(Rank.SIX)],
            TRUMP,
        )
        self.assertEqual(result.points, 4 + 3 + 2 + 11 + 10 + 0)


class InvalidTrickTests(unittest.TestCase):
    """Check that impossible tricks are refused loudly."""

    def test_response_length_must_match(self) -> None:
        with self.assertRaises(ValueError):
            beating_pairs(
                [hearts(Rank.KING), hearts(Rank.QUEEN)], [hearts(Rank.ACE)], TRUMP
            )

    def test_invalid_lead_raises(self) -> None:
        with self.assertRaises(ValueError):
            resolve_trick(
                [hearts(Rank.KING), clubs(Rank.KING)],
                [spades(Rank.SIX), spades(Rank.SEVEN)],
                TRUMP,
            )

    def test_same_card_cannot_be_played_twice(self) -> None:
        with self.assertRaises(ValueError):
            resolve_trick([hearts(Rank.KING)], [hearts(Rank.KING)], TRUMP)


if __name__ == "__main__":
    unittest.main()
