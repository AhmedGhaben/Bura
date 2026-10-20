"""Text and ordering rules the screen needs, kept free of Pygame."""

from collections.abc import Iterable

from bura.actions import Action, Lead, Respond
from bura.cards import Card
from bura.dealing import Seat
from bura.game import Deal, DealResult, EndReason, Phase
from bura.view import PlayerView


def seat_name(seat: Seat) -> str:
    """Return the name shown for a seat, such as ``"Player 1"``."""

    return f"Player {seat + 1}"


def sort_hand(cards: Iterable[Card]) -> list[Card]:
    """Order cards by suit, then from the strongest rank down."""

    return sorted(cards, key=lambda card: (card.suit.value, -card.rank))


def find_action(deal: Deal, seat: Seat, selected: Iterable[Card]) -> Action | None:
    """Return the legal lead or response made of exactly the selected cards.

    Return None when the selection is not a legal move, so the screen can keep
    the Play button disabled. The order of the selected cards does not matter.
    """

    chosen: set[Card] = set(selected)
    if not chosen:
        return None
    for action in deal.legal_actions(seat):
        if isinstance(action, Lead | Respond) and set(action.cards) == chosen:
            return action
    return None


def selection_hint(view: PlayerView) -> str:
    """Return one line telling the player what to do now."""

    if view.phase is Phase.LEAD:
        return "Your lead: pick 1 to 3 cards of the same suit, then press Play."
    count: int = len(view.table_lead)
    noun: str = "card" if count == 1 else "cards"
    return f"Your answer: pick {count} {noun} (any suits), then press Play."


def result_lines(result: DealResult) -> list[str]:
    """Describe how a hand ended, for the hand-over-hand result screen."""

    winner: str = seat_name(result.winner) if result.winner is not None else ""
    claimant: str = seat_name(result.claimant) if result.claimant is not None else ""
    if result.reason is EndReason.CORRECT_CLAIM:
        return [
            f"{claimant} claimed 31 and had {result.claimant_points} points.",
            f"{winner} wins the hand.",
        ]
    if result.reason is EndReason.FALSE_CLAIM:
        return [
            f"{claimant} claimed 31 but had only {result.claimant_points} points.",
            f"{winner} wins the hand.",
        ]
    if result.reason is EndReason.BURA:
        return [f"{winner} holds three trumps (a Bura).", f"{winner} wins the hand."]
    return ["All cards were played and nobody claimed.", "The hand is void."]
