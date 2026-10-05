"""Pygame window for the Bura table; gameplay will be connected later."""

import pygame


WINDOW_SIZE: tuple[int, int] = (960, 700)
FELT: tuple[int, int, int] = (22, 86, 67)
FELT_LIGHT: tuple[int, int, int] = (31, 105, 82)
CREAM: tuple[int, int, int] = (242, 232, 208)
MUTED: tuple[int, int, int] = (180, 210, 194)
GOLD: tuple[int, int, int] = (210, 169, 94)


class BuraWindow:
    """Display the table and handle window events for the initial UI."""

    def __init__(self) -> None:
        """Open the window and load the fonts."""

        pygame.init()
        self._screen: pygame.Surface = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Bura Card Game")
        self._clock: pygame.time.Clock = pygame.time.Clock()
        self._title_font: pygame.font.Font = pygame.font.SysFont("segoeui", 34, bold=True)
        self._label_font: pygame.font.Font = pygame.font.SysFont("segoeui", 23)
        self._small_font: pygame.font.Font = pygame.font.SysFont("segoeui", 17)

    def run(self) -> None:
        """Keep the window open until it is closed or Escape is pressed."""

        running: bool = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            self._draw()
            pygame.display.flip()
            self._clock.tick(60)

        pygame.quit()

    def _text(
        self,
        message: str,
        x: int,
        y: int,
        *,
        color: tuple[int, int, int] = CREAM,
        small: bool = False,
    ) -> None:
        font: pygame.font.Font = self._small_font if small else self._label_font
        rendered: pygame.Surface = font.render(message, True, color)
        self._screen.blit(rendered, rendered.get_rect(center=(x, y)))

    def _card_slot(self, x: int, y: int, *, face_down: bool = False) -> None:
        card: pygame.Rect = pygame.Rect(x, y, 80, 112)
        if face_down:
            pygame.draw.rect(self._screen, CREAM, card, border_radius=9)
            pygame.draw.rect(self._screen, GOLD, card.inflate(-12, -12), 2, border_radius=5)
            self._text("B", card.centerx, card.centery, color=FELT, small=True)
        else:
            pygame.draw.rect(self._screen, MUTED, card, 2, border_radius=9)

    def _draw(self) -> None:
        self._screen.fill(FELT)
        pygame.draw.rect(
            self._screen,
            FELT_LIGHT,
            pygame.Rect(24, 24, 912, 652),
            border_radius=28,
        )
        pygame.draw.rect(
            self._screen,
            GOLD,
            pygame.Rect(24, 24, 912, 652),
            3,
            border_radius=28,
        )

        title: pygame.Surface = self._title_font.render("BURA", True, CREAM)
        self._screen.blit(title, title.get_rect(center=(480, 64)))

        self._text("Opponent's hand", 480, 120, small=True)
        for x in (344, 440, 536):
            self._card_slot(x, 148, face_down=True)

        self._text("Draw pile", 165, 312, small=True)
        self._card_slot(125, 335, face_down=True)
        self._text("Trump", 280, 312, small=True)
        self._card_slot(240, 335)

        self._text("Trick area", 620, 312, small=True)
        for x in (530, 626):
            self._card_slot(x, 335)

        self._text("Your hand", 480, 479, small=True)
        for x in (344, 440, 536):
            self._card_slot(x, 505)

        self._text("Table preview - dealing and turns come next", 480, 650, color=MUTED, small=True)


def main() -> None:
    """Start the Bura window."""

    BuraWindow().run()
