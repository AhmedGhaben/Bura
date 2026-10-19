"""The action types are small, comparable values."""

import unittest

from bura.actions import Claim, Lead, Respond
from bura.cards import Card, Rank, Suit


class ActionTests(unittest.TestCase):
    """Check that equal actions compare equal and can be stored in sets."""

    def test_actions_compare_by_cards(self) -> None:
        card: Card = Card(Suit.HEARTS, Rank.ACE)
        self.assertEqual(Lead((card,)), Lead((card,)))
        self.assertNotEqual(Lead((card,)), Respond((card,)))
        self.assertEqual(Claim(), Claim())

    def test_actions_can_be_put_in_a_set(self) -> None:
        card: Card = Card(Suit.CLUBS, Rank.SIX)
        actions: set[Lead | Respond | Claim] = {Lead((card,)), Lead((card,)), Claim()}
        self.assertEqual(len(actions), 2)


if __name__ == "__main__":
    unittest.main()
