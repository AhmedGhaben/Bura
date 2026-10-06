"""A shuffled 36-card Bura deck."""

from random import Random

from bura.cards import Card, Rank, Suit


class Deck:
    """Own a shuffled pack with one card of every suit and Bura rank."""

    def __init__(self, rng: Random | None = None) -> None:
        """Create all 36 cards and shuffle them, using ``rng`` if given."""
        cards: list[Card] = [Card(suit, rank) for suit in Suit for rank in Rank]
        (rng if rng is not None else Random()).shuffle(cards)
        self._cards: list[Card] = cards

    @property
    def remaining(self) -> int:
        """Return the number of cards not yet drawn."""

        return len(self._cards)

    def draw(self) -> Card:
        """Take the next card, raising ValueError when the pack is empty."""

        if not self._cards:
            raise ValueError("Cannot draw from an empty deck")
        return self._cards.pop()
