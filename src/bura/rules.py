"""Rules for comparing cards in a single-card Bura trick."""

from bura.cards import Card, Suit


def beats(challenger: Card, lead: Card, trump_suit: Suit) -> bool:
    """Return whether the challenger beats the led card in one trick.

    A higher card of the led suit wins. A trump beats any non-trump card.
    A card in an unrelated non-trump suit cannot beat the lead.
    """

    if challenger.suit == lead.suit:
        return challenger.rank > lead.rank

    return challenger.suit == trump_suit and lead.suit != trump_suit
