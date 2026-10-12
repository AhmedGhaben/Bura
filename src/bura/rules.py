"""Rules for comparing cards and resolving Bura tricks."""

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import permutations

from bura.cards import Card, Suit, trick_points

MAX_TRICK_CARDS: int = 3


def beats(challenger: Card, lead: Card, trump_suit: Suit) -> bool:
    """Return whether the challenger beats the led card in one trick.

    A higher card of the led suit wins. A trump beats any non-trump card.
    A card in an unrelated non-trump suit cannot beat the lead.
    """

    if challenger.suit == lead.suit:
        return challenger.rank > lead.rank

    return challenger.suit == trump_suit and lead.suit != trump_suit


def is_valid_lead(cards: Sequence[Card]) -> bool:
    """Return whether the cards form a legal lead.

    A lead is one, two or three different cards, all of the same suit.
    """

    return (
        1 <= len(cards) <= MAX_TRICK_CARDS
        and len(set(cards)) == len(cards)
        and len({card.suit for card in cards}) == 1
    )


def beating_pairs(
    lead: Sequence[Card],
    response: Sequence[Card],
    trump_suit: Suit,
) -> tuple[tuple[Card, Card], ...] | None:
    """Match each led card with a different response card that beats it.

    Return ``(led_card, response_card)`` pairs when every led card can be
    beaten by its own response card, in any order. Return ``None`` when no
    such matching exists. Raise ``ValueError`` if the lead is not legal, the
    response has a different number of cards, or a card appears twice.
    """

    if not is_valid_lead(lead):
        raise ValueError(f"Invalid lead: {[str(card) for card in lead]}")
    if len(response) != len(lead):
        raise ValueError("The response must have as many cards as the lead")
    if len(set(response)) != len(response) or set(response) & set(lead):
        raise ValueError("A card cannot be played twice in one trick")

    for ordering in permutations(response):
        if all(
            beats(answer, led, trump_suit)
            for led, answer in zip(lead, ordering, strict=True)
        ):
            return tuple(zip(lead, ordering, strict=True))
    return None


@dataclass(frozen=True, slots=True)
class TrickResult:
    """The outcome of one completed trick."""

    lead: tuple[Card, ...]
    response: tuple[Card, ...]
    responder_wins: bool
    pairs: tuple[tuple[Card, Card], ...]

    @property
    def cards(self) -> tuple[Card, ...]:
        """Return every card played to the trick, lead first."""

        return self.lead + self.response

    @property
    def points(self) -> int:
        """Return the points the trick winner captures."""

        return trick_points(self.cards)


def resolve_trick(
    lead: Sequence[Card],
    response: Sequence[Card],
    trump_suit: Suit,
) -> TrickResult:
    """Decide who wins a trick.

    The responder wins only if every led card is beaten by a different
    response card; otherwise the leader wins. ``pairs`` shows which card
    beat which, and is empty when the leader wins.
    """

    pairs: tuple[tuple[Card, Card], ...] | None = beating_pairs(
        lead, response, trump_suit
    )
    return TrickResult(
        lead=tuple(lead),
        response=tuple(response),
        responder_wins=pairs is not None,
        pairs=pairs if pairs is not None else (),
    )
