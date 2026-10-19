"""The moves a player can make during a hand of Bura."""

from dataclasses import dataclass

from bura.cards import Card


@dataclass(frozen=True, slots=True)
class Lead:
    """Start a trick by playing one to three cards of a single suit."""

    cards: tuple[Card, ...]


@dataclass(frozen=True, slots=True)
class Respond:
    """Answer a lead by playing the same number of cards."""

    cards: tuple[Card, ...]


@dataclass(frozen=True, slots=True)
class Claim:
    """Stop the hand by claiming to hold at least 31 points."""


Action = Lead | Respond | Claim
