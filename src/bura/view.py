"""What one player is allowed to see of a hand in progress."""

from dataclasses import dataclass

from bura.cards import Card
from bura.dealing import Seat
from bura.game import Deal, Phase
from bura.rules import TrickResult


@dataclass(frozen=True, slots=True)
class PlayerView:
    """A snapshot of the table from one player's seat.

    It holds only what that player may know: their own hand, the face-up
    cards, and counts of everything hidden. Captured cards are shown only as
    counts, because players may not look back at their tricks to count points.
    Bots and the screen get a view, never the hand itself.
    """

    seat: Seat
    hand: tuple[Card, ...]
    trump_card: Card
    trump_card_in_stock: bool
    stock_size: int
    opponent_hand_size: int
    table_lead: tuple[Card, ...]
    own_captured_count: int
    opponent_captured_count: int
    to_act: Seat | None
    phase: Phase
    last_trick: TrickResult | None

    @property
    def is_my_turn(self) -> bool:
        """Return whether this player must act now."""

        return self.to_act is self.seat


def view_for(deal: Deal, seat: Seat) -> PlayerView:
    """Build the view of the hand as the given player sees it."""

    return PlayerView(
        seat=seat,
        hand=deal.hand(seat),
        trump_card=deal.trump_card,
        trump_card_in_stock=deal.trump_card_in_stock,
        stock_size=deal.stock_size,
        opponent_hand_size=len(deal.hand(seat.other)),
        table_lead=deal.table_lead,
        own_captured_count=len(deal.captured(seat)),
        opponent_captured_count=len(deal.captured(seat.other)),
        to_act=deal.to_act,
        phase=deal.phase,
        last_trick=deal.last_trick,
    )
