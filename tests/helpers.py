"""Shortcuts for building cards and scripted hands in tests."""

from bura.cards import Card, Rank, Suit
from bura.dealing import DealSetup, Seat
from bura.deck import Deck
from bura.game import Deal

R: dict[str, Rank] = {
    "6": Rank.SIX,
    "7": Rank.SEVEN,
    "8": Rank.EIGHT,
    "9": Rank.NINE,
    "J": Rank.JACK,
    "Q": Rank.QUEEN,
    "K": Rank.KING,
    "10": Rank.TEN,
    "A": Rank.ACE,
}
S: dict[str, Suit] = {
    "C": Suit.CLUBS,
    "D": Suit.DIAMONDS,
    "H": Suit.HEARTS,
    "S": Suit.SPADES,
}


def c(text: str) -> Card:
    """Build a card from text such as ``"10H"`` (ten of hearts)."""

    return Card(S[text[-1]], R[text[:-1]])


def cs(*texts: str) -> tuple[Card, ...]:
    """Build several cards from text."""

    return tuple(c(text) for text in texts)


def scripted_deal(
    hand_one: tuple[str, ...],
    hand_two: tuple[str, ...],
    stock: tuple[str, ...],
    trump_card: str = "9S",
    dealer: Seat = Seat.ONE,
) -> Deal:
    """Build a hand with chosen cards.

    ``stock`` lists the stock from top to bottom; the trump card is added as
    its bottom card. With the default dealer, seat TWO leads first.
    """

    trump: Card = c(trump_card)
    setup: DealSetup = DealSetup(
        dealer=dealer,
        hands=(cs(*hand_one), cs(*hand_two)),
        trump_card=trump,
    )
    return Deal(setup, Deck.from_cards([*cs(*stock), trump]))
