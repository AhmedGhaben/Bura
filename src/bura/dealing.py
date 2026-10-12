"""Seats at the table and the opening deal of a Bura hand."""

from dataclasses import dataclass
from enum import IntEnum

from bura.cards import Card, Suit
from bura.deck import DECK_SIZE, Deck

HAND_SIZE: int = 3


class Seat(IntEnum):
    """One of the two places at the table."""

    ONE = 0
    TWO = 1

    @property
    def other(self) -> "Seat":
        """Return the opponent's seat."""

        return Seat.TWO if self is Seat.ONE else Seat.ONE


@dataclass(frozen=True, slots=True)
class DealSetup:
    """The cards each player holds and the trump card after dealing."""

    dealer: Seat
    hands: tuple[tuple[Card, ...], tuple[Card, ...]]
    trump_card: Card

    @property
    def trump_suit(self) -> Suit:
        """Return the suit of the face-up trump card."""

        return self.trump_card.suit

    @property
    def first_leader(self) -> Seat:
        """Return the player who leads the first trick (the non-dealer)."""

        return self.dealer.other

    def hand(self, seat: Seat) -> tuple[Card, ...]:
        """Return the cards dealt to the given seat."""

        return self.hands[seat]


def deal(deck: Deck, dealer: Seat) -> DealSetup:
    """Deal three cards to each player and turn up the trump card.

    Cards go out one at a time, non-dealer first. The next card is the
    trump card; it is placed at the bottom of the deck so it is drawn last.
    The deck must be full.
    """

    if deck.remaining != DECK_SIZE:
        raise ValueError("A deal needs a full deck")

    dealt: dict[Seat, list[Card]] = {Seat.ONE: [], Seat.TWO: []}
    for _ in range(HAND_SIZE):
        for seat in (dealer.other, dealer):
            dealt[seat].append(deck.draw())

    trump_card: Card = deck.draw()
    deck.put_on_bottom(trump_card)

    return DealSetup(
        dealer=dealer,
        hands=(tuple(dealt[Seat.ONE]), tuple(dealt[Seat.TWO])),
        trump_card=trump_card,
    )
