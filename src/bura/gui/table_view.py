"""Drawing the Bura table from a player's view."""

from collections.abc import Collection

import pygame

from bura.cards import Card
from bura.dealing import Seat
from bura.game import Phase
from bura.presentation import seat_name, sort_hand
from bura.rules import TrickResult
from bura.view import PlayerView

from .widgets import (
    CARD_SIZE,
    CREAM,
    FELT,
    FELT_LIGHT,
    GOLD,
    MUTED,
    SMALL_CARD_SIZE,
    Fonts,
    draw_card_back,
    draw_card_face,
    draw_empty_slot,
    draw_suit,
)

WINDOW_SIZE: tuple[int, int] = (960, 700)
CENTER_X: int = WINDOW_SIZE[0] // 2
HAND_GAP: int = 16
HAND_Y: int = 492
RAISE: int = 18
OPPONENT_Y: int = 128
ROW_GAP: int = 12
LEAD_Y: int = 252
ANSWER_Y: int = 352
ROWS_CENTER_X: int = 570


def centered_row(
    count: int, size: tuple[int, int], center_x: int, y: int, gap: int
) -> list[pygame.Rect]:
    """Return the rectangles of ``count`` cards laid out in a centred row."""

    width, height = size
    total: int = count * width + max(count - 1, 0) * gap
    left: int = center_x - total // 2
    return [pygame.Rect(left + i * (width + gap), y, width, height) for i in range(count)]


class TableRenderer:
    """Draw the table for one player, and say where their cards are."""

    def __init__(self, screen: pygame.Surface, fonts: Fonts) -> None:
        """Remember the surface to draw on and the fonts to use."""

        self._screen: pygame.Surface = screen
        self._fonts: Fonts = fonts

    @staticmethod
    def hand_rects(count: int) -> list[pygame.Rect]:
        """Return where a hand of ``count`` cards is drawn (not raised)."""

        return centered_row(count, CARD_SIZE, CENTER_X, HAND_Y, HAND_GAP)

    def _text(
        self,
        message: str,
        center: tuple[int, int],
        font: pygame.font.Font,
        color: tuple[int, int, int] = CREAM,
    ) -> None:
        rendered: pygame.Surface = font.render(message, True, color)
        self._screen.blit(rendered, rendered.get_rect(center=center))

    def draw_table(
        self,
        view: PlayerView,
        *,
        scores: tuple[int, int],
        target: int,
        deal_number: int,
        selected: Collection[Card] = (),
        message: str = "",
        trick: TrickResult | None = None,
    ) -> None:
        """Draw everything the player may see.

        When ``trick`` is given, the table shows that finished trick instead
        of the cards currently on the table.
        """

        screen: pygame.Surface = self._screen
        screen.fill(FELT)
        panel: pygame.Rect = pygame.Rect(24, 24, 912, 652)
        pygame.draw.rect(screen, FELT_LIGHT, panel, border_radius=28)
        pygame.draw.rect(screen, GOLD, panel, 3, border_radius=28)

        self._text(f"BURA   Hand {deal_number}   First to {target}", (CENTER_X, 52), self._fonts.title)
        self._text(
            f"{seat_name(Seat.ONE)}: {scores[0]}      {seat_name(Seat.TWO)}: {scores[1]}",
            (CENTER_X, 90),
            self._fonts.label,
            GOLD,
        )

        self._draw_opponent(view)
        self._draw_stock_and_trump(view)
        self._draw_piles(view)
        self._draw_rows(view, trick)
        self._draw_hand(view, selected)
        if message:
            self._text(message, (CENTER_X, 462), self._fonts.small, MUTED)

    def _draw_opponent(self, view: PlayerView) -> None:
        opponent: Seat = view.seat.other
        count: int = view.opponent_hand_size
        noun: str = "card" if count == 1 else "cards"
        self._text(f"{seat_name(opponent)}: {count} {noun}", (CENTER_X, 124), self._fonts.small)
        for rect in centered_row(count, CARD_SIZE, CENTER_X, OPPONENT_Y + 6, HAND_GAP):
            draw_card_back(self._screen, rect)

    def _draw_stock_and_trump(self, view: PlayerView) -> None:
        stock: pygame.Rect = pygame.Rect(70, 270, *CARD_SIZE)
        trump: pygame.Rect = pygame.Rect(170, 270, *CARD_SIZE)
        if view.stock_size:
            draw_card_back(self._screen, stock)
        else:
            draw_empty_slot(self._screen, stock)
        self._text(f"Stock: {view.stock_size}", (stock.centerx, stock.bottom + 18), self._fonts.small)

        if view.trump_card_in_stock:
            draw_card_face(self._screen, trump, view.trump_card, self._fonts)
            self._text("Trump", (trump.centerx, trump.bottom + 18), self._fonts.small, GOLD)
        else:
            draw_empty_slot(self._screen, trump)
            draw_suit(self._screen, view.trump_card.suit, trump.center, 22, CREAM)
            self._text("Trump suit", (trump.centerx, trump.bottom + 18), self._fonts.small, GOLD)

    def _draw_piles(self, view: PlayerView) -> None:
        mine: int = view.own_captured_count
        theirs: int = view.opponent_captured_count
        self._text("Your tricks", (850, 282), self._fonts.small, MUTED)
        self._text(f"{mine} cards", (850, 306), self._fonts.small)
        self._text(f"{seat_name(view.seat.other)}'s tricks", (850, 352), self._fonts.small, MUTED)
        self._text(f"{theirs} cards", (850, 376), self._fonts.small)

    def _draw_rows(self, view: PlayerView, trick: TrickResult | None) -> None:
        lead: tuple[Card, ...]
        answer: tuple[Card, ...]
        if trick is not None:
            lead, answer = trick.lead, trick.response
        else:
            lead, answer = view.table_lead, ()
        slots: int = len(answer) if trick is not None else len(lead)

        self._text("Lead", (ROWS_CENTER_X - 190, LEAD_Y + 45), self._fonts.small, MUTED)
        self._text("Answer", (ROWS_CENTER_X - 190, ANSWER_Y + 45), self._fonts.small, MUTED)

        lead_rects: list[pygame.Rect] = centered_row(
            len(lead), SMALL_CARD_SIZE, ROWS_CENTER_X, LEAD_Y, ROW_GAP
        )
        for card, rect in zip(lead, lead_rects, strict=True):
            draw_card_face(self._screen, rect, card, self._fonts)

        answer_rects: list[pygame.Rect] = centered_row(
            slots, SMALL_CARD_SIZE, ROWS_CENTER_X, ANSWER_Y, ROW_GAP
        )
        for index, rect in enumerate(answer_rects):
            if index < len(answer):
                draw_card_face(self._screen, rect, answer[index], self._fonts)
            else:
                draw_empty_slot(self._screen, rect)

    def _draw_hand(self, view: PlayerView, selected: Collection[Card]) -> None:
        cards: list[Card] = sort_hand(view.hand)
        self._text(f"{seat_name(view.seat)}", (190, HAND_Y + 56), self._fonts.label, GOLD)
        self._text("(you)", (190, HAND_Y + 82), self._fonts.small, MUTED)
        for card, rect in zip(cards, self.hand_rects(len(cards)), strict=True):
            raised: bool = card in selected
            if raised:
                rect = rect.move(0, -RAISE)
            draw_card_face(self._screen, rect, card, self._fonts, selected=raised)

    def card_at(self, view: PlayerView, position: tuple[int, int]) -> Card | None:
        """Return the hand card under a mouse position, if any."""

        if view.phase is Phase.FINISHED:
            return None
        cards: list[Card] = sort_hand(view.hand)
        for card, rect in zip(cards, self.hand_rects(len(cards)), strict=True):
            if rect.move(0, -RAISE).union(rect).collidepoint(position):
                return card
        return None
