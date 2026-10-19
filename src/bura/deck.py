"""A shuffled 36-card Bura deck."""

from collections.abc import Iterable
from random import Random

from bura.cards import Card, Rank, Suit

DECK_SIZE: int = len(Suit) * len(Rank)


class Deck:
    """Own a shuffled pack with one card of every suit and Bura rank.

    Cards are drawn from the top. The bottom card is drawn last, which is
    where the face-up trump card goes after the deal.
    """

    def __init__(self, rng: Random | None = None) -> None:
        """Create all 36 cards and shuffle them, using ``rng`` if given."""

        cards: list[Card] = [Card(suit, rank) for suit in Suit for rank in Rank]
        (rng if rng is not None else Random()).shuffle(cards)
        # The end of the list is the top of the pack; index 0 is the bottom.
        self._cards: list[Card] = cards

    @classmethod
    def from_cards(cls, cards: Iterable[Card]) -> "Deck":
        """Build a deck holding exactly these cards, first card on top.

        The first card given is the first one drawn and the last card given
        is the bottom of the pack. Nothing is shuffled. This is for tests,
        saved games and replays; it may hold fewer than 36 cards.
        """

        ordered: list[Card] = list(cards)
        if len(set(ordered)) != len(ordered):
            raise ValueError("A deck cannot hold the same card twice")
        deck: Deck = cls(Random(0))
        deck._cards = ordered[::-1]
        return deck

    @property
    def remaining(self) -> int:
        """Return the number of cards not yet drawn."""

        return len(self._cards)

    @property
    def bottom_card(self) -> Card | None:
        """Return the card that will be drawn last, or None when empty."""

        return self._cards[0] if self._cards else None

    def draw(self) -> Card:
        """Take the top card, raising ValueError when the pack is empty."""

        if not self._cards:
            raise ValueError("Cannot draw from an empty deck")
        return self._cards.pop()

    def put_on_bottom(self, card: Card) -> None:
        """Place a card under the pack so that it is drawn last."""

        if card in self._cards:
            raise ValueError(f"{card} is already in the deck")
        self._cards.insert(0, card)
