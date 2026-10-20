"""A match: scoring, dealers, and when it ends."""

import unittest
from random import Random

from bura.actions import Action, Claim
from bura.dealing import Seat
from bura.game import Deal, EndReason, Phase
from bura.match import Match


def fresh_match(target: int = 3) -> Match:
    """Return a match whose first hand is still in play."""

    for seed in range(100):
        match: Match = Match(Seat.ONE, target, Random(seed))
        if match.deal.phase is not Phase.FINISHED:
            return match
    raise AssertionError("no seed gave a playable first hand")


def play_without_claims(match: Match, rng: Random) -> None:
    """Finish the current hand with random moves, never claiming."""

    while match.deal.to_act is not None:
        seat: Seat | None = match.deal.to_act
        assert seat is not None
        moves: list[Action] = [
            move
            for move in match.deal.legal_actions(seat)
            if not isinstance(move, Claim)
        ]
        match.apply(seat, rng.choice(moves))


class MatchTests(unittest.TestCase):
    """Check scores, dealers and the end of the match."""

    def test_a_new_match_starts_at_zero(self) -> None:
        match: Match = fresh_match()

        self.assertEqual(match.scores, (0, 0))
        self.assertEqual(match.target, 3)
        self.assertEqual(match.deal_number, 1)
        self.assertIs(match.deal.dealer, Seat.ONE)
        self.assertIsNone(match.winner)
        self.assertFalse(match.is_over)

    def test_a_false_claim_scores_for_the_other_player_and_the_claimant_deals(
        self,
    ) -> None:
        match: Match = fresh_match()
        claimant: Seat | None = match.deal.to_act
        assert claimant is not None
        match.apply(claimant, Claim())

        result = match.deal.result
        assert result is not None
        self.assertIs(result.reason, EndReason.FALSE_CLAIM)
        scores: list[int] = [0, 0]
        scores[claimant.other] = 1
        self.assertEqual(match.scores, (scores[0], scores[1]))

        next_hand: Deal = match.next_deal()
        self.assertIs(next_hand.dealer, claimant)
        self.assertEqual(match.deal_number, 2)

    def test_a_void_hand_scores_nothing_and_the_dealer_deals_again(self) -> None:
        for seed in range(200):
            match: Match = Match(Seat.TWO, 3, Random(seed))
            if match.deal.phase is Phase.FINISHED:
                continue
            play_without_claims(match, Random(seed))
            result = match.deal.result
            assert result is not None
            if result.reason is EndReason.EXHAUSTED:
                self.assertEqual(match.scores, (0, 0))
                self.assertIs(match.next_deal().dealer, Seat.TWO)
                return
        self.fail("no void hand found")

    def test_a_bura_counts_as_a_won_hand(self) -> None:
        for seed in range(2000):
            match: Match = Match(Seat.ONE, 3, Random(seed))
            result = match.deal.result
            if result is not None and result.reason is EndReason.BURA:
                self.assertEqual(sum(match.scores), 1)
                assert result.winner is not None
                self.assertEqual(match.scores[result.winner], 1)
                return
        self.fail("no Bura found in the first 2000 deals")

    def test_the_match_ends_when_a_player_reaches_the_target(self) -> None:
        match: Match = fresh_match(target=1)
        claimant: Seat | None = match.deal.to_act
        assert claimant is not None
        match.apply(claimant, Claim())

        self.assertTrue(match.is_over)
        self.assertIs(match.winner, claimant.other)
        with self.assertRaises(ValueError):
            match.next_deal()

    def test_next_deal_needs_a_finished_hand(self) -> None:
        match: Match = fresh_match()
        with self.assertRaises(ValueError):
            match.next_deal()

    def test_target_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            Match(target=0)

    def test_a_whole_match_of_random_hands_finishes(self) -> None:
        rng: Random = Random(4)
        match: Match = Match(Seat.ONE, 3, rng)
        for _ in range(500):
            play_without_claims(match, rng)
            if match.is_over:
                break
            match.next_deal()
        self.assertTrue(match.is_over)
        self.assertEqual(max(match.scores), 3)


if __name__ == "__main__":
    unittest.main()
