"""Cards, trick-taking rank order, and point values for 36-card Bura."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, IntEnum


class Suit(str, Enum):
    """The four suits in the deck."""

    CLUBS = "clubs"
    DIAMONDS = "diamonds"
    HEARTS = "hearts"
    SPADES = "spades"

    @property
    def symbol(self) -> str:
        """Return the suit's printed symbol, such as ``♥``."""

        return {
            Suit.CLUBS: "♣",
            Suit.DIAMONDS: "♦",
            Suit.HEARTS: "♥",
            Suit.SPADES: "♠",
        }[self]


class Rank(IntEnum):
    """Ranks in ascending trick-taking order (10 beats King).

    The numeric values are strength positions, not face values:
    ``Rank.TEN`` is 7. Use ``label`` for display.
    """

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

    @property
    def label(self) -> str:
        """Return the printed face value, such as ``"10"`` or ``"K"``."""

        return {
            Rank.SIX: "6",
            Rank.SEVEN: "7",
            Rank.EIGHT: "8",
            Rank.NINE: "9",
            Rank.JACK: "J",
            Rank.QUEEN: "Q",
            Rank.KING: "K",
            Rank.TEN: "10",
            Rank.ACE: "A",
        }[self]


@dataclass(frozen=True, slots=True)
class Card:
    """An immutable playing card with suit, rank, and Bura point value."""

    suit: Suit
    rank: Rank

    def __post_init__(self) -> None:
        """Reject anything that is not a real Suit and Rank."""

        if not isinstance(self.suit, Suit):
            raise TypeError(f"suit must be a Suit, got {self.suit!r}")
        if not isinstance(self.rank, Rank):
            raise TypeError(f"rank must be a Rank, got {self.rank!r}")

    def __str__(self) -> str:
        """Return a short label such as ``10♥``."""

        return f"{self.rank.label}{self.suit.symbol}"

    @property
    def points(self) -> int:
        """Return the card's value when captured in a trick."""

        return self.rank.points


def trick_points(cards: Iterable[Card]) -> int:
    """Sum the captured card points in a trick or group of tricks."""

    return sum(card.points for card in cards)