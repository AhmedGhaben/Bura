"""Pygame window for the Bura table; gameplay will be connected later."""

import pygame


# --- Window ---
WINDOW_WIDTH: int = 960
WINDOW_HEIGHT: int = 700
WINDOW_SIZE: tuple[int, int] = (WINDOW_WIDTH, WINDOW_HEIGHT)
WINDOW_CENTER_X: int = WINDOW_WIDTH // 2
WINDOW_TITLE: str = "Bura Card Game"
FPS: int = 60

# --- Colors ---
FELT: tuple[int, int, int] = (22, 86, 67)
FELT_LIGHT: tuple[int, int, int] = (31, 105, 82)
CREAM: tuple[int, int, int] = (242, 232, 208)
MUTED: tuple[int, int, int] = (180, 210, 194)
GOLD: tuple[int, int, int] = (210, 169, 94)

# --- Fonts ---
FONT_NAME: str = "segoeui"
TITLE_FONT_SIZE: int = 34
LABEL_FONT_SIZE: int = 23
SMALL_FONT_SIZE: int = 17

# --- Table ---
TABLE_MARGIN: int = 24
TABLE_RECT: pygame.Rect = pygame.Rect(
    TABLE_MARGIN,
    TABLE_MARGIN,
    WINDOW_WIDTH - 2 * TABLE_MARGIN,
    WINDOW_HEIGHT - 2 * TABLE_MARGIN,
)
TABLE_RADIUS: int = 28
TABLE_BORDER_WIDTH: int = 3

# --- Cards ---
CARD_WIDTH: int = 80
CARD_HEIGHT: int = 112
CARD_RADIUS: int = 9
CARD_SPACING: int = 96
SLOT_BORDER_WIDTH: int = 2
CARD_BACK_INSET: int = 12
CARD_BACK_BORDER_WIDTH: int = 2
CARD_BACK_INNER_RADIUS: int = 5
CARD_BACK_LETTER: str = "B"

# --- Layout: title ---
TITLE_TEXT: str = "BURA"
TITLE_Y: int = 64

# --- Layout: opponent hand ---
OPPONENT_LABEL_Y: int = 120
OPPONENT_CARDS_Y: int = 148

# --- Layout: middle row (draw pile, trump, trick area) ---
MIDDLE_LABEL_Y: int = 312
MIDDLE_CARDS_Y: int = 335
DRAW_PILE_LABEL_X: int = 165
DRAW_PILE_X: int = 125
TRUMP_LABEL_X: int = 280
TRUMP_X: int = 240
TRICK_LABEL_X: int = 620
TRICK_FIRST_X: int = 530
TRICK_SLOTS: int = 2

# --- Layout: player hand ---
PLAYER_LABEL_Y: int = 479
PLAYER_CARDS_Y: int = 505

# --- Layout: hands ---
HAND_FIRST_X: int = 344
HAND_SIZE: int = 3

# --- Layout: footer ---
FOOTER_Y: int = 650
FOOTER_TEXT: str = "Table preview - dealing and turns come next"


class BuraWindow:
    """Display the table and handle window events for the initial UI."""

    def __init__(self) -> None:
        """Open the window and load the fonts."""

        pygame.init()
        self._screen: pygame.Surface = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(WINDOW_TITLE)
        self._clock: pygame.time.Clock = pygame.time.Clock()
        self._title_font: pygame.font.Font = pygame.font.SysFont(FONT_NAME, TITLE_FONT_SIZE, bold=True)
        self._label_font: pygame.font.Font = pygame.font.SysFont(FONT_NAME, LABEL_FONT_SIZE)
        self._small_font: pygame.font.Font = pygame.font.SysFont(FONT_NAME, SMALL_FONT_SIZE)

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
            self._clock.tick(FPS)

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
        card: pygame.Rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        if face_down:
            pygame.draw.rect(self._screen, CREAM, card, border_radius=CARD_RADIUS)
            pygame.draw.rect(
                self._screen,
                GOLD,
                card.inflate(-CARD_BACK_INSET, -CARD_BACK_INSET),
                CARD_BACK_BORDER_WIDTH,
                border_radius=CARD_BACK_INNER_RADIUS,
            )
            self._text(CARD_BACK_LETTER, card.centerx, card.centery, color=FELT, small=True)
        else:
            pygame.draw.rect(self._screen, MUTED, card, SLOT_BORDER_WIDTH, border_radius=CARD_RADIUS)

    def _draw(self) -> None:
        self._screen.fill(FELT)
        pygame.draw.rect(
            self._screen,
            FELT_LIGHT,
            TABLE_RECT,
            border_radius=TABLE_RADIUS,
        )
        pygame.draw.rect(
            self._screen,
            GOLD,
            TABLE_RECT,
            TABLE_BORDER_WIDTH,
            border_radius=TABLE_RADIUS,
        )

        title: pygame.Surface = self._title_font.render(TITLE_TEXT, True, CREAM)
        self._screen.blit(title, title.get_rect(center=(WINDOW_CENTER_X, TITLE_Y)))

        self._text("Opponent's hand", WINDOW_CENTER_X, OPPONENT_LABEL_Y, small=True)
        for i in range(HAND_SIZE):
            self._card_slot(HAND_FIRST_X + i * CARD_SPACING, OPPONENT_CARDS_Y, face_down=True)

        self._text("Draw pile", DRAW_PILE_LABEL_X, MIDDLE_LABEL_Y, small=True)
        self._card_slot(DRAW_PILE_X, MIDDLE_CARDS_Y, face_down=True)
        self._text("Trump", TRUMP_LABEL_X, MIDDLE_LABEL_Y, small=True)
        self._card_slot(TRUMP_X, MIDDLE_CARDS_Y)

        self._text("Trick area", TRICK_LABEL_X, MIDDLE_LABEL_Y, small=True)
        for i in range(TRICK_SLOTS):
            self._card_slot(TRICK_FIRST_X + i * CARD_SPACING, MIDDLE_CARDS_Y)

        self._text("Your hand", WINDOW_CENTER_X, PLAYER_LABEL_Y, small=True)
        for i in range(HAND_SIZE):
            self._card_slot(HAND_FIRST_X + i * CARD_SPACING, PLAYER_CARDS_Y)

        self._text(FOOTER_TEXT, WINDOW_CENTER_X, FOOTER_Y, color=MUTED, small=True)


def main() -> None:
    """Start the Bura window."""

    BuraWindow().run()