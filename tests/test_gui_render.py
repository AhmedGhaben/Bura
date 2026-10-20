"""The table can be drawn for every kind of view without errors."""

import os
import unittest
from random import Random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
from helpers import cs, scripted_deal  # noqa: E402

from bura.actions import Lead, Respond  # noqa: E402
from bura.dealing import Seat  # noqa: E402
from bura.game import Deal  # noqa: E402
from bura.gui.table_view import WINDOW_SIZE, TableRenderer  # noqa: E402
from bura.gui.widgets import make_fonts  # noqa: E402
from bura.view import view_for  # noqa: E402


class RenderTests(unittest.TestCase):
    """Draw the table into an off-screen surface."""

    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    def setUp(self) -> None:
        self.surface: pygame.Surface = pygame.Surface(WINDOW_SIZE)
        self.renderer: TableRenderer = TableRenderer(self.surface, make_fonts())

    def test_a_fresh_deal_draws(self) -> None:
        deal: Deal = Deal.start(Seat.ONE, Random(2))
        for seat in (Seat.ONE, Seat.TWO):
            self.renderer.draw_table(
                view_for(deal, seat), scores=(0, 0), target=3, deal_number=1
            )

    def test_a_lead_selection_and_a_finished_trick_draw(self) -> None:
        deal: Deal = scripted_deal(
            ("6C", "7D", "8H"), ("KH", "QH", "6D"), ("9D", "8D", "7D", "6H", "9H")
        )
        deal.apply(Seat.TWO, Lead(cs("KH", "QH")))
        view = view_for(deal, Seat.ONE)
        self.renderer.draw_table(
            view,
            scores=(1, 0),
            target=3,
            deal_number=2,
            selected=set(cs("6C")),
            message="hello",
        )
        trick = deal.apply(Seat.ONE, Respond(cs("6C", "8H")))
        self.renderer.draw_table(
            view_for(deal, Seat.ONE),
            scores=(1, 0),
            target=3,
            deal_number=2,
            trick=trick,
        )

    def test_the_stock_runs_out_and_the_trump_card_is_gone(self) -> None:
        deal: Deal = scripted_deal(("6C", "7D", "8H"), ("KH", "QD", "6D"), ("9D",))
        deal.apply(Seat.TWO, Lead(cs("KH")))
        deal.apply(Seat.ONE, Respond(cs("6C")))
        self.renderer.draw_table(
            view_for(deal, Seat.TWO), scores=(0, 0), target=3, deal_number=1
        )

    def test_cards_are_found_by_position(self) -> None:
        deal: Deal = Deal.start(Seat.ONE, Random(2))
        view = view_for(deal, Seat.ONE)
        rects = TableRenderer.hand_rects(3)
        found = self.renderer.card_at(view, rects[0].center)
        self.assertIsNotNone(found)
        self.assertIsNone(self.renderer.card_at(view, (5, 5)))


if __name__ == "__main__":
    unittest.main()
