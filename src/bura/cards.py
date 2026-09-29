"""Cards, trick-taking rank order, and point values for 36-card Bura."""

from dataclasses import dataclass
from enum import Enum, IntEnum
from collections.abc import Iterable


class Suit(str, Enum):
    """The four suits in the deck."""

    CLUBS = "clubs"
    DIAMONDS = "diamonds"
    HEARTS = "hearts"
    SPADES = "spades"


class Rank(IntEnum):
    """Ranks in ascending trick-taking order (10 beats King)."""

    SIX = 0
    SEVEN = 1
    EIGHT = 2
    NINE = 3
    JACK = 4
    QUEEN = 5
    KING = 6
    TEN = 7
    ACE = 8

    @property
    def points(self) -> int:
        """Return the points this rank contributes to a won trick."""

        return {
            Rank.JACK: 2,
            Rank.QUEEN: 3,
            Rank.KING: 4,
            Rank.TEN: 10,
            Rank.ACE: 11,
        }.get(self, 0)


@dataclass(frozen=True, slots=True)
class Card:
    """An immutable playing card with suit, rank, and Bura point value."""

    suit: Suit
    rank: Rank

    @property
    def points(self) -> int:
        """Return the card's value when captured in a trick."""

        return self.rank.points


def trick_points(cards: Iterable[Card]) -> int:
    """Sum the captured card points in a trick or group of tricks."""

    return sum(card.points for card in cards)
