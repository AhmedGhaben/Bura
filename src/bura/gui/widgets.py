"""Colours, fonts, card drawing and buttons for the Pygame interface."""

from dataclasses import dataclass

import pygame

from bura.cards import Card, Suit

RGB = tuple[int, int, int]

FELT: RGB = (22, 86, 67)
FELT_LIGHT: RGB = (31, 105, 82)
FELT_DARK: RGB = (14, 58, 45)
CREAM: RGB = (242, 232, 208)
MUTED: RGB = (180, 210, 194)
GOLD: RGB = (210, 169, 94)
RED: RGB = (196, 32, 40)
INK: RGB = (28, 28, 34)
DISABLED: RGB = (88, 120, 106)

CARD_SIZE: tuple[int, int] = (80, 112)
SMALL_CARD_SIZE: tuple[int, int] = (64, 90)


@dataclass(frozen=True)
class Fonts:
    """The fonts used on screen."""

    title: pygame.font.Font
    label: pygame.font.Font
    small: pygame.font.Font
    card: pygame.font.Font
    card_small: pygame.font.Font


def make_fonts() -> Fonts:
    """Create the fonts. Pygame's font module must already be initialised."""

    return Fonts(
        title=pygame.font.SysFont("segoeui", 34, bold=True),
        label=pygame.font.SysFont("segoeui", 23),
        small=pygame.font.SysFont("segoeui", 17),
        card=pygame.font.SysFont("segoeui", 24, bold=True),
        card_small=pygame.font.SysFont("segoeui", 19, bold=True),
    )


def suit_color(suit: Suit) -> RGB:
    """Return red for hearts and diamonds, near-black for clubs and spades."""

    return RED if suit in (Suit.HEARTS, Suit.DIAMONDS) else INK


def draw_suit(
    surface: pygame.Surface,
    suit: Suit,
    center: tuple[int, int],
    size: int,
    color: RGB | None = None,
) -> None:
    """Draw a suit symbol with shapes, so no special font is needed."""

    ink: RGB = color if color is not None else suit_color(suit)
    x, y = center
    s: float = float(size)

    def circle(dx: float, dy: float, r: float) -> None:
        pygame.draw.circle(surface, ink, (round(x + dx * s), round(y + dy * s)), round(r * s))

    def polygon(points: list[tuple[float, float]]) -> None:
        pygame.draw.polygon(
            surface, ink, [(round(x + px * s), round(y + py * s)) for px, py in points]
        )

    if suit is Suit.DIAMONDS:
        polygon([(0, -1.0), (0.7, 0), (0, 1.0), (-0.7, 0)])
    elif suit is Suit.HEARTS:
        circle(-0.5, -0.4, 0.52)
        circle(0.5, -0.4, 0.52)
        polygon([(-0.99, -0.2), (0.99, -0.2), (0, 1.0)])
    elif suit is Suit.SPADES:
        circle(-0.5, 0.2, 0.52)
        circle(0.5, 0.2, 0.52)
        polygon([(-0.99, 0.0), (0.99, 0.0), (0, -1.0)])
        polygon([(0, 0.2), (-0.38, 1.0), (0.38, 1.0)])
    else:
        circle(0, -0.5, 0.46)
        circle(-0.55, 0.25, 0.46)
        circle(0.55, 0.25, 0.46)
        polygon([(0, 0), (-0.38, 1.0), (0.38, 1.0)])


def draw_card_face(
    surface: pygame.Surface,
    rect: pygame.Rect,
    card: Card,
    fonts: Fonts,
    *,
    selected: bool = False,
    highlight: bool = False,
) -> None:
    """Draw a face-up card."""

    pygame.draw.rect(surface, CREAM, rect, border_radius=9)
    border: RGB = GOLD if (selected or highlight) else INK
    pygame.draw.rect(surface, border, rect, 4 if selected or highlight else 1, border_radius=9)
    small: bool = rect.height < 100
    font: pygame.font.Font = fonts.card_small if small else fonts.card
    color: RGB = suit_color(card.suit)
    label: pygame.Surface = font.render(card.rank.label, True, color)
    surface.blit(label, (rect.x + 7, rect.y + 4))
    draw_suit(
        surface,
        card.suit,
        (rect.x + 13, rect.y + 4 + label.get_height() + 9),
        6 if small else 7,
    )
    draw_suit(surface, card.suit, rect.center, rect.width // 4 + (2 if not small else 0))


def draw_card_back(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Draw a face-down card."""

    pygame.draw.rect(surface, CREAM, rect, border_radius=9)
    pygame.draw.rect(surface, FELT_DARK, rect.inflate(-10, -10), border_radius=6)
    pygame.draw.rect(surface, GOLD, rect.inflate(-18, -18), 2, border_radius=4)


def draw_empty_slot(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Draw an empty outline where a card can go."""

    pygame.draw.rect(surface, MUTED, rect, 2, border_radius=9)


@dataclass
class Button:
    """A rectangular button that can be switched off."""

    key: str
    label: str
    rect: pygame.Rect
    enabled: bool = True

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button."""

        fill: RGB = GOLD if self.enabled else FELT_DARK
        ink: RGB = INK if self.enabled else DISABLED
        pygame.draw.rect(surface, fill, self.rect, border_radius=10)
        text: pygame.Surface = font.render(self.label, True, ink)
        surface.blit(text, text.get_rect(center=self.rect.center))

    def hit(self, position: tuple[int, int]) -> bool:
        """Return whether a click at this position presses the button."""

        return self.enabled and self.rect.collidepoint(position)
