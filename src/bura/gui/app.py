"""The Bura application: menu, hand-over screens, the table and the results."""

import logging
from enum import Enum
from random import Random

import pygame

from bura.actions import Action, Claim, Lead, Respond
from bura.cards import Card
from bura.dealing import Seat
from bura.game import Deal, Phase
from bura.log_config import configure_logging
from bura.match import Match
from bura.presentation import find_action, result_lines, seat_name, selection_hint
from bura.rules import TrickResult
from bura.view import PlayerView, view_for

from .table_view import CENTER_X, WINDOW_SIZE, TableRenderer
from .widgets import (
    CREAM,
    FELT,
    FELT_DARK,
    FELT_LIGHT,
    GOLD,
    MUTED,
    Button,
    Fonts,
    make_fonts,
)

logger: logging.Logger = logging.getLogger(__name__)

MAX_SELECTED: int = 3


class Screen(Enum):
    """Which screen the application is showing."""

    MENU = "menu"
    HANDOFF = "handoff"
    PLAY = "play"
    TRICK = "trick"
    HAND_RESULT = "hand result"
    MATCH_RESULT = "match result"


def wide_button(key: str, label: str, y: int, *, enabled: bool = True) -> Button:
    """Return a centred button of the standard menu size."""

    return Button(key, label, pygame.Rect(CENTER_X - 150, y, 300, 56), enabled)


class BuraApp:
    """A two-player game on one screen, with a hand-over screen between turns.

    Every rule is decided by the engine; this class only draws and turns
    clicks into engine actions.
    """

    def __init__(self, rng: Random | None = None) -> None:
        """Open the window. ``rng`` makes the shuffles reproducible."""

        pygame.init()
        self._screen: pygame.Surface = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Bura Card Game")
        self._clock: pygame.time.Clock = pygame.time.Clock()
        self._fonts: Fonts = make_fonts()
        self._renderer: TableRenderer = TableRenderer(self._screen, self._fonts)
        self._rng: Random | None = rng

        self._kind: Screen = Screen.MENU
        self._match: Match | None = None
        self._viewer: Seat | None = None
        self._pending: Seat = Seat.ONE
        self._selected: set[Card] = set()
        self._confirm_claim: bool = False
        self._trick: TrickResult | None = None
        self._quit: bool = False

    # --- information for the main loop and for tests -------------------

    @property
    def kind(self) -> Screen:
        """Return which screen is showing."""

        return self._kind

    @property
    def match(self) -> Match | None:
        """Return the match in progress, if any."""

        return self._match

    @property
    def viewer(self) -> Seat | None:
        """Return the player currently looking at the screen, if any."""

        return self._viewer

    @property
    def selected(self) -> frozenset[Card]:
        """Return the cards currently raised in the player's hand."""

        return frozenset(self._selected)

    @property
    def wants_quit(self) -> bool:
        """Return whether the player chose to quit."""

        return self._quit

    @property
    def renderer(self) -> TableRenderer:
        """Return the table renderer (used to locate cards on screen)."""

        return self._renderer

    # --- running --------------------------------------------------------

    def run(self) -> None:
        """Keep the window open until it is closed, or Escape is pressed."""

        while not self._quit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._quit = True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.click(event.pos)
            self.draw()
            pygame.display.flip()
            self._clock.tick(60)
        pygame.quit()

    # --- buttons and clicks ---------------------------------------------

    def buttons(self) -> list[Button]:
        """Return the buttons of the current screen."""

        if self._kind is Screen.MENU:
            return [
                wide_button("new_game", "New 2-player match", 300),
                wide_button("quit", "Quit", 376),
            ]
        if self._kind is Screen.HANDOFF:
            return [wide_button("ready", f"I am {seat_name(self._pending)}", 420)]
        if self._kind is Screen.PLAY:
            return self._play_buttons()
        if self._kind is Screen.TRICK:
            return [Button("continue", "Continue", pygame.Rect(700, 500, 190, 46))]
        if self._kind is Screen.HAND_RESULT:
            label: str = "See match result" if self._require_match().is_over else "Next hand"
            return [wide_button("next", label, 460)]
        return [
            wide_button("new_game", "New match", 360),
            wide_button("menu", "Main menu", 436),
        ]

    def _play_buttons(self) -> list[Button]:
        if self._confirm_claim:
            return [
                Button("claim_yes", "Yes, claim 31", pygame.Rect(CENTER_X - 210, 400, 200, 50)),
                Button("claim_no", "No, go back", pygame.Rect(CENTER_X + 10, 400, 200, 50)),
            ]
        playable: bool = self._current_action() is not None
        return [
            Button("play", "Play", pygame.Rect(700, 500, 190, 46), playable),
            Button("claim", "Claim 31", pygame.Rect(700, 556, 190, 46)),
        ]

    def button_rect(self, key: str) -> pygame.Rect:
        """Return the rectangle of the button with the given key."""

        for button in self.buttons():
            if button.key == key:
                return button.rect
        raise KeyError(key)

    def click(self, position: tuple[int, int]) -> None:
        """Handle a left click at a screen position."""

        for button in self.buttons():
            if button.hit(position):
                self._press(button.key)
                return
        if self._kind is Screen.PLAY and not self._confirm_claim:
            card: Card | None = self._renderer.card_at(self._current_view(), position)
            if card is not None:
                self._toggle(card)

    def _toggle(self, card: Card) -> None:
        if card in self._selected:
            self._selected.remove(card)
        elif len(self._selected) < MAX_SELECTED:
            self._selected.add(card)

    def _press(self, key: str) -> None:
        if key == "new_game":
            self._start_match()
        elif key == "quit":
            self._quit = True
        elif key == "menu":
            self._kind = Screen.MENU
        elif key == "ready":
            self._viewer = self._pending
            self._selected.clear()
            self._kind = Screen.PLAY
        elif key == "play":
            self._play_selected()
        elif key == "claim":
            self._confirm_claim = True
        elif key == "claim_no":
            self._confirm_claim = False
        elif key == "claim_yes":
            self._confirm_claim = False
            self._act(Claim())
        elif key == "continue":
            self._after_trick()
        elif key == "next":
            self._next_hand()

    # --- game flow --------------------------------------------------------

    def _require_match(self) -> Match:
        if self._match is None:
            raise RuntimeError("There is no match in progress")
        return self._match

    def _start_match(self) -> None:
        self._match = Match(Seat.ONE, rng=self._rng)
        self._after_deal_start()

    def _after_deal_start(self) -> None:
        deal: Deal = self._require_match().deal
        self._viewer = None
        self._selected.clear()
        if deal.phase is Phase.FINISHED:
            self._kind = Screen.HAND_RESULT
        else:
            self._go_to(deal.to_act)

    def _go_to(self, seat: Seat | None) -> None:
        """Show the table to a player, with a hand-over screen if needed."""

        if seat is None:
            self._viewer = None
            self._kind = Screen.HAND_RESULT
        elif seat is self._viewer:
            self._selected.clear()
            self._kind = Screen.PLAY
        else:
            self._viewer = None
            self._pending = seat
            self._kind = Screen.HANDOFF

    def _current_view(self) -> PlayerView:
        if self._viewer is None:
            raise RuntimeError("Nobody is looking at the table")
        return view_for(self._require_match().deal, self._viewer)

    def _current_action(self) -> Action | None:
        if self._viewer is None:
            return None
        return find_action(self._require_match().deal, self._viewer, self._selected)

    def _play_selected(self) -> None:
        action: Action | None = self._current_action()
        if action is not None:
            self._act(action)

    def _act(self, action: Action) -> None:
        match_: Match = self._require_match()
        seat: Seat | None = self._viewer
        if seat is None:
            return
        logger.info("%s plays %s", seat_name(seat), type(action).__name__)
        trick: TrickResult | None = match_.apply(seat, action)
        self._selected.clear()
        deal: Deal = match_.deal
        if isinstance(action, Respond):
            self._trick = trick
            self._kind = Screen.TRICK
        elif isinstance(action, Lead):
            self._go_to(deal.to_act)
        else:
            self._viewer = None
            self._kind = Screen.HAND_RESULT

    def _after_trick(self) -> None:
        deal: Deal = self._require_match().deal
        self._trick = None
        if deal.phase is Phase.FINISHED:
            self._viewer = None
            self._kind = Screen.HAND_RESULT
        else:
            self._go_to(deal.to_act)

    def _next_hand(self) -> None:
        match_: Match = self._require_match()
        if match_.is_over:
            self._kind = Screen.MATCH_RESULT
        else:
            match_.next_deal()
            self._after_deal_start()

    # --- drawing -----------------------------------------------------------

    def draw(self) -> None:
        """Draw the current screen."""

        if self._kind in (Screen.PLAY, Screen.TRICK):
            self._draw_table()
        else:
            self._draw_plain()
        for button in self.buttons():
            button.draw(self._screen, self._fonts.label)

    def _text(
        self,
        message: str,
        center: tuple[int, int],
        font: pygame.font.Font,
        color: tuple[int, int, int] = CREAM,
    ) -> None:
        rendered: pygame.Surface = font.render(message, True, color)
        self._screen.blit(rendered, rendered.get_rect(center=center))

    def _draw_table(self) -> None:
        match_: Match = self._require_match()
        view: PlayerView = self._current_view()
        message: str = ""
        trick: TrickResult | None = None
        if self._kind is Screen.PLAY:
            message = selection_hint(view)
        elif self._trick is not None:
            trick = self._trick
            winner: Seat = view.seat if trick.responder_wins else view.seat.other
            message = f"{seat_name(winner)} wins the trick."
        self._renderer.draw_table(
            view,
            scores=match_.scores,
            target=match_.target,
            deal_number=match_.deal_number,
            selected=self._selected,
            message=message,
            trick=trick,
        )
        if self._confirm_claim:
            self._draw_claim_question()

    def _draw_claim_question(self) -> None:
        box: pygame.Rect = pygame.Rect(CENTER_X - 260, 280, 520, 190)
        pygame.draw.rect(self._screen, FELT_DARK, box, border_radius=18)
        pygame.draw.rect(self._screen, GOLD, box, 3, border_radius=18)
        self._text("Claim 31 points?", (CENTER_X, 316), self._fonts.title)
        self._text(
            "If you have fewer than 31 points you lose the hand.",
            (CENTER_X, 364),
            self._fonts.small,
            MUTED,
        )

    def _draw_plain(self) -> None:
        screen: pygame.Surface = self._screen
        screen.fill(FELT)
        panel: pygame.Rect = pygame.Rect(24, 24, 912, 652)
        pygame.draw.rect(screen, FELT_LIGHT, panel, border_radius=28)
        pygame.draw.rect(screen, GOLD, panel, 3, border_radius=28)

        if self._kind is Screen.MENU:
            self._text("BURA", (CENTER_X, 170), self._fonts.title)
            self._text("A two-player card game on one screen", (CENTER_X, 224), self._fonts.label, MUTED)
        elif self._kind is Screen.HANDOFF:
            name: str = seat_name(self._pending)
            self._text(f"Pass the device to {name}", (CENTER_X, 250), self._fonts.title)
            self._text(
                f"Only {name} should look at the next screen.",
                (CENTER_X, 310),
                self._fonts.label,
                MUTED,
            )
        elif self._kind is Screen.HAND_RESULT:
            self._draw_hand_result()
        else:
            self._draw_match_result()

    def _draw_hand_result(self) -> None:
        match_: Match = self._require_match()
        result = match_.deal.result
        self._text(f"Hand {match_.deal_number} finished", (CENTER_X, 150), self._fonts.title)
        if result is not None:
            for index, line in enumerate(result_lines(result)):
                self._text(line, (CENTER_X, 230 + index * 36), self._fonts.label)
        one, two = match_.scores
        self._text(
            f"Score:  {seat_name(Seat.ONE)} {one}  -  {two} {seat_name(Seat.TWO)}",
            (CENTER_X, 360),
            self._fonts.label,
            GOLD,
        )
        self._text(f"First to {match_.target} wins the match", (CENTER_X, 400), self._fonts.small, MUTED)

    def _draw_match_result(self) -> None:
        match_: Match = self._require_match()
        winner: Seat | None = match_.winner
        headline: str = f"{seat_name(winner)} wins the match!" if winner is not None else "Match over"
        self._text(headline, (CENTER_X, 190), self._fonts.title)
        one, two = match_.scores
        self._text(
            f"Final score:  {seat_name(Seat.ONE)} {one}  -  {two} {seat_name(Seat.TWO)}",
            (CENTER_X, 260),
            self._fonts.label,
            GOLD,
        )


def main() -> None:
    """Start the Bura application."""

    configure_logging()
    BuraApp().run()
