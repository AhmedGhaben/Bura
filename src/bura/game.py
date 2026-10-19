"""One hand of Bura: turns, tricks, drawing cards, and how the hand ends."""

from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from random import Random
from typing import Self

from bura.actions import Action, Lead, Respond
from bura.cards import Card, Suit
from bura.dealing import DealSetup, Seat, deal
from bura.deck import Deck
from bura.rules import MAX_TRICK_CARDS, TrickResult, is_valid_lead, resolve_trick


class Phase(Enum):
    """What the hand is waiting for."""

    LEAD = "lead"
    RESPOND = "respond"
    FINISHED = "finished"


class EndReason(Enum):
    """Why a hand ended."""

    CORRECT_CLAIM = "correct claim"
    FALSE_CLAIM = "false claim"
    EXHAUSTED = "all cards played"


@dataclass(frozen=True, slots=True)
class DealResult:
    """How a hand ended. ``winner`` is None when nobody won (a void hand)."""

    winner: Seat | None
    reason: EndReason
    claimant: Seat | None = None
    claimant_points: int | None = None


class IllegalActionError(ValueError):
    """Raised when a player tries something the rules do not allow."""


class Deal:
    """The state of one hand, and the only place its rules are applied.

    Ask ``legal_actions`` what a player may do and pass the chosen action to
    ``apply``. Nothing else changes the hand.
    """

    def __init__(self, setup: DealSetup, stock: Deck) -> None:
        """Start a hand from an opening deal and the stock left after it."""

        self._dealer: Seat = setup.dealer
        self._trump_card: Card = setup.trump_card
        self._stock: Deck = stock
        self._hands: list[list[Card]] = [list(hand) for hand in setup.hands]
        self._captured: list[list[Card]] = [[], []]
        self._set_aside: list[Card] = []
        self._leader: Seat = setup.first_leader
        self._lead: tuple[Card, ...] = ()
        self._phase: Phase = Phase.LEAD
        self._result: DealResult | None = None
        self._last_trick: TrickResult | None = None

    @classmethod
    def start(cls, dealer: Seat, rng: Random | None = None) -> Self:
        """Shuffle a new pack, deal it, and return the hand ready to play."""

        deck: Deck = Deck(rng)
        return cls(deal(deck, dealer), deck)

    @property
    def dealer(self) -> Seat:
        """Return the player who dealt."""

        return self._dealer

    @property
    def trump_card(self) -> Card:
        """Return the face-up card that shows the trump suit."""

        return self._trump_card

    @property
    def trump_suit(self) -> Suit:
        """Return the trump suit."""

        return self._trump_card.suit

    @property
    def trump_card_in_stock(self) -> bool:
        """Return whether the trump card is still waiting at the stock's bottom."""

        return self._stock.bottom_card == self._trump_card

    @property
    def phase(self) -> Phase:
        """Return what the hand is waiting for."""

        return self._phase

    @property
    def leader(self) -> Seat:
        """Return who leads the current trick (the last trick's winner)."""

        return self._leader

    @property
    def to_act(self) -> Seat | None:
        """Return the player who must act now, or None once the hand is over."""

        if self._phase is Phase.LEAD:
            return self._leader
        if self._phase is Phase.RESPOND:
            return self._leader.other
        return None

    @property
    def table_lead(self) -> tuple[Card, ...]:
        """Return the cards led and waiting for an answer (empty otherwise)."""

        return self._lead

    @property
    def stock_size(self) -> int:
        """Return how many cards are left in the stock."""

        return self._stock.remaining

    @property
    def set_aside(self) -> tuple[Card, ...]:
        """Return the stock cards that were never used."""

        return tuple(self._set_aside)

    @property
    def last_trick(self) -> TrickResult | None:
        """Return the most recent finished trick, if any."""

        return self._last_trick

    @property
    def result(self) -> DealResult | None:
        """Return how the hand ended, or None while it is still going."""

        return self._result

    def hand(self, seat: Seat) -> tuple[Card, ...]:
        """Return the cards a player holds."""

        return tuple(self._hands[seat])

    def captured(self, seat: Seat) -> tuple[Card, ...]:
        """Return the cards a player has won in tricks."""

        return tuple(self._captured[seat])

    def legal_actions(self, seat: Seat) -> list[Action]:
        """Return every action the given player may take right now."""

        if self.to_act is not seat:
            return []
        hand: list[Card] = self._hands[seat]
        actions: list[Action] = []
        if self._phase is Phase.LEAD:
            for size in range(1, min(MAX_TRICK_CARDS, len(hand)) + 1):
                for cards in combinations(hand, size):
                    if is_valid_lead(cards):
                        actions.append(Lead(cards))
        else:
            for cards in combinations(hand, len(self._lead)):
                actions.append(Respond(cards))
        return actions

    def apply(self, seat: Seat, action: Action) -> TrickResult | None:
        """Carry out an action for a player.

        Return the finished trick when this action completes one, otherwise
        None. Raise ``IllegalActionError`` and change nothing if the action is
        not allowed.
        """

        if self._phase is Phase.FINISHED:
            raise IllegalActionError("The hand is over")
        if seat is not self.to_act:
            raise IllegalActionError(f"It is not {seat.name}'s turn")

        match action:
            case Lead(cards=cards):
                self._play_lead(seat, cards)
                return None
            case Respond(cards=cards):
                return self._play_response(seat, cards)
            case _:
                raise IllegalActionError(f"{action!r} is not available yet")

    def _check_cards_in_hand(self, seat: Seat, cards: tuple[Card, ...]) -> None:
        """Raise unless the cards are different and all in the player's hand."""

        hand: list[Card] = self._hands[seat]
        if len(set(cards)) != len(cards):
            raise IllegalActionError("A card cannot be played twice")
        if not all(card in hand for card in cards):
            raise IllegalActionError("You can only play cards from your hand")

    def _play_lead(self, seat: Seat, cards: tuple[Card, ...]) -> None:
        """Put a lead on the table."""

        if self._phase is not Phase.LEAD:
            raise IllegalActionError("A lead is already on the table")
        self._check_cards_in_hand(seat, cards)
        if not is_valid_lead(cards):
            raise IllegalActionError("A lead is 1 to 3 cards of one suit")
        for card in cards:
            self._hands[seat].remove(card)
        self._lead = cards
        self._phase = Phase.RESPOND

    def _play_response(self, seat: Seat, cards: tuple[Card, ...]) -> TrickResult:
        """Answer the lead, decide the trick, and draw new cards."""

        if self._phase is not Phase.RESPOND:
            raise IllegalActionError("There is no lead to answer")
        if len(cards) != len(self._lead):
            raise IllegalActionError("Play as many cards as were led")
        self._check_cards_in_hand(seat, cards)
        for card in cards:
            self._hands[seat].remove(card)

        result: TrickResult = resolve_trick(self._lead, cards, self.trump_suit)
        winner: Seat = seat if result.responder_wins else seat.other
        self._captured[winner].extend(result.cards)
        self._last_trick = result
        self._lead = ()
        self._leader = winner
        self._refill(winner, len(cards))
        self._phase = Phase.LEAD

        if not self._hands[Seat.ONE] and not self._hands[Seat.TWO]:
            self._finish(DealResult(winner=None, reason=EndReason.EXHAUSTED))
        return result

    def _refill(self, winner: Seat, count: int) -> None:
        """Draw back up to three cards, the trick winner drawing first.

        If the stock cannot give each player ``count`` cards, whatever is
        left is set aside unused and play continues from the hands.
        """

        if self._stock.remaining < 2 * count:
            while self._stock.remaining:
                self._set_aside.append(self._stock.draw())
            return
        for _ in range(count):
            for seat in (winner, winner.other):
                self._hands[seat].append(self._stock.draw())

    def _finish(self, result: DealResult) -> None:
        """Record the result and stop the hand."""

        self._result = result
        self._phase = Phase.FINISHED
