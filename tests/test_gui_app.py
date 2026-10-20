"""Playing the whole application by clicking, without a visible window."""

import os
import unittest
from random import Random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from bura.actions import Action, Lead, Respond  # noqa: E402
from bura.cards import Card  # noqa: E402
from bura.dealing import Seat  # noqa: E402
from bura.game import Deal, Phase  # noqa: E402
from bura.gui.app import BuraApp, Screen  # noqa: E402
from bura.match import Match  # noqa: E402
from bura.presentation import sort_hand  # noqa: E402


def press(app: BuraApp, key: str) -> None:
    """Click the middle of a button."""

    app.click(app.button_rect(key).center)


def click_card(app: BuraApp, card: Card) -> None:
    """Click a card in the viewer's hand."""

    seat: Seat | None = app.viewer
    assert seat is not None and app.match is not None
    cards: list[Card] = sort_hand(app.match.deal.hand(seat))
    rect: pygame.Rect = app.renderer.hand_rects(len(cards))[cards.index(card)]
    app.click(rect.center)


def start_match(seed: int) -> BuraApp:
    """Open the app and start a match that is not decided by a dealt Bura."""

    for attempt in range(seed, seed + 200):
        app: BuraApp = BuraApp(Random(attempt))
        press(app, "new_game")
        if app.kind is Screen.HANDOFF:
            return app
    raise AssertionError("no playable first hand found")


def play_one_action(app: BuraApp, rng: Random) -> None:
    """Make a random legal lead or response using only clicks."""

    assert app.match is not None and app.viewer is not None
    deal: Deal = app.match.deal
    moves: list[Action] = [
        move for move in deal.legal_actions(app.viewer) if isinstance(move, Lead | Respond)
    ]
    move: Action = rng.choice(moves)
    assert isinstance(move, Lead | Respond)
    for card in move.cards:
        click_card(app, card)
    press(app, "play")


def play_match_by_clicking(app: BuraApp, rng: Random) -> None:
    """Click through a whole match, sometimes claiming 31."""

    for _ in range(20000):
        app.draw()
        kind: Screen = app.kind
        if kind is Screen.MATCH_RESULT:
            return
        if kind is Screen.MENU:
            press(app, "new_game")
        elif kind is Screen.HANDOFF:
            press(app, "ready")
        elif kind is Screen.PLAY:
            if rng.random() < 0.15:
                press(app, "claim")
                app.draw()
                press(app, "claim_yes")
            else:
                play_one_action(app, rng)
        elif kind is Screen.TRICK:
            press(app, "continue")
        else:
            press(app, "next")
    raise AssertionError("the match did not finish")


class AppFlowTests(unittest.TestCase):
    """Check the screens and what clicking does."""

    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    def test_the_menu_starts_a_match_and_quit_quits(self) -> None:
        app: BuraApp = BuraApp(Random(1))
        self.assertIs(app.kind, Screen.MENU)
        press(app, "quit")
        self.assertTrue(app.wants_quit)

    def test_a_new_match_starts_with_a_hand_over_screen(self) -> None:
        app: BuraApp = start_match(1)

        self.assertIsNone(app.viewer)
        assert app.match is not None
        self.assertEqual(app.match.scores, (0, 0))
        press(app, "ready")
        self.assertIs(app.kind, Screen.PLAY)
        self.assertIs(app.viewer, app.match.deal.to_act)

    def test_cards_cannot_be_clicked_on_the_hand_over_screen(self) -> None:
        app: BuraApp = start_match(1)
        for rect in app.renderer.hand_rects(3):
            app.click(rect.center)
        self.assertIs(app.kind, Screen.HANDOFF)
        self.assertEqual(app.selected, frozenset())

    def test_play_is_enabled_only_for_a_legal_selection(self) -> None:
        for seed in range(100):
            app: BuraApp = start_match(seed)
            press(app, "ready")
            assert app.match is not None and app.viewer is not None
            hand: list[Card] = sort_hand(app.match.deal.hand(app.viewer))
            other_suit: list[Card] = [c for c in hand if c.suit is not hand[0].suit]
            if not other_suit:
                continue

            play = next(b for b in app.buttons() if b.key == "play")
            self.assertFalse(play.enabled)
            click_card(app, hand[0])
            self.assertEqual(app.selected, frozenset({hand[0]}))
            self.assertTrue(next(b for b in app.buttons() if b.key == "play").enabled)

            click_card(app, other_suit[0])
            self.assertFalse(next(b for b in app.buttons() if b.key == "play").enabled)
            click_card(app, other_suit[0])
            self.assertEqual(app.selected, frozenset({hand[0]}))
            return
        self.fail("no hand with two suits found")

    def test_a_lead_hands_over_to_the_responder_who_then_sees_the_result(self) -> None:
        app: BuraApp = start_match(2)
        press(app, "ready")
        assert app.match is not None and app.viewer is not None
        leader: Seat = app.viewer
        play_one_action(app, Random(0))

        self.assertIs(app.kind, Screen.HANDOFF)
        self.assertIsNone(app.viewer)
        press(app, "ready")
        self.assertIs(app.viewer, leader.other)
        play_one_action(app, Random(0))

        self.assertIs(app.kind, Screen.TRICK)
        app.draw()
        press(app, "continue")
        self.assertIn(app.kind, (Screen.PLAY, Screen.HANDOFF, Screen.HAND_RESULT))

    def test_claiming_asks_first_and_can_be_cancelled(self) -> None:
        app: BuraApp = start_match(3)
        press(app, "ready")

        press(app, "claim")
        app.draw()
        self.assertEqual({b.key for b in app.buttons()}, {"claim_yes", "claim_no"})
        press(app, "claim_no")
        self.assertIs(app.kind, Screen.PLAY)
        self.assertEqual({b.key for b in app.buttons()}, {"play", "claim"})

    def test_a_false_claim_ends_the_hand_and_scores(self) -> None:
        app: BuraApp = start_match(3)
        press(app, "ready")
        assert app.match is not None
        claimant: Seat | None = app.viewer
        assert claimant is not None
        press(app, "claim")
        press(app, "claim_yes")

        self.assertIs(app.kind, Screen.HAND_RESULT)
        self.assertIs(app.match.deal.phase, Phase.FINISHED)
        expected: list[int] = [0, 0]
        expected[claimant.other] = 1
        self.assertEqual(app.match.scores, (expected[0], expected[1]))
        app.draw()
        press(app, "next")
        self.assertIn(app.kind, (Screen.HANDOFF, Screen.HAND_RESULT))
        self.assertIs(app.match.deal.dealer, claimant)

    def test_a_whole_match_can_be_played_by_clicking(self) -> None:
        for seed in (1, 2, 3):
            app: BuraApp = start_match(seed)
            play_match_by_clicking(app, Random(seed))

            match: Match | None = app.match
            assert match is not None
            self.assertTrue(match.is_over)
            self.assertEqual(max(match.scores), match.target)
            press(app, "menu")
            self.assertIs(app.kind, Screen.MENU)

    def test_a_card_click_during_a_claim_question_does_nothing(self) -> None:
        app: BuraApp = start_match(3)
        press(app, "ready")
        press(app, "claim")
        for rect in app.renderer.hand_rects(3):
            app.click(rect.center)
        self.assertEqual(app.selected, frozenset())


if __name__ == "__main__":
    unittest.main()
