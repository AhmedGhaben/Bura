"""Pygame window showing a real deal; clicking to play comes in the next step."""

from random import Random

import pygame

from bura.dealing import Seat
from bura.game import Deal
from bura.view import view_for

from .table_view import WINDOW_SIZE, TableRenderer
from .widgets import Fonts, make_fonts


class BuraWindow:
    """Show a freshly dealt hand from Player 1's seat."""

    def __init__(self) -> None:
        """Open the window and load the fonts."""

        pygame.init()
        self._screen: pygame.Surface = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Bura Card Game")
        self._clock: pygame.time.Clock = pygame.time.Clock()
        fonts: Fonts = make_fonts()
        self._renderer: TableRenderer = TableRenderer(self._screen, fonts)
        self._deal: Deal = Deal.start(Seat.ONE, Random())

    def run(self) -> None:
        """Keep the window open until it is closed or Escape is pressed."""

        running: bool = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._deal = Deal.start(Seat.ONE, Random())

            self.draw()
            pygame.display.flip()
            self._clock.tick(60)

        pygame.quit()

    def draw(self) -> None:
        """Draw the current deal."""

        self._renderer.draw_table(
            view_for(self._deal, Seat.ONE),
            scores=(0, 0),
            target=3,
            deal_number=1,
            message="Preview of a real deal. Click for a new one. Playing comes next.",
        )


def main() -> None:
    """Start the Bura window."""

    BuraWindow().run()
