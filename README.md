# Bura Card Game

A Python project for the Python Development Practice course. Two people can
play a full match of two-player Bura on one shared screen, with a hand-over
screen between turns. Computer opponents are the next milestone.

## Rules used in this project

We implement two-player Bura with a 36-card pack, following
[Pagat](https://www.pagat.com/aceten/bura.html). The course table describes
Bura as having "trump bidding"; the Pagat two-player rules have no bidding,
and neither does this game.

**Cards.** Ranks from low to high: 6, 7, 8, 9, J, Q, K, 10, A. Points:
J = 2, Q = 3, K = 4, 10 = 10, A = 11, others 0. The pack holds 120 points.

**Deal.** The dealer gives 3 cards to each player, one at a time, non-dealer
first. The next card is turned face up to show trump and lies at the bottom
of the stock, so it is the last card drawn. The non-dealer leads first.

**Tricks.** The leader plays 1, 2 or 3 cards of one suit. The responder plays
the same number of cards, any cards, with no need to follow suit. A card is
beaten by a higher card of its suit or by any trump. The responder wins the
trick only if every led card is beaten by a different response card, in any
order; otherwise the leader wins. The winner takes all the cards and leads
next. Cards are played face up.

**Drawing.** After each trick, the winner draws first, then the players
alternate until both hold 3 cards. If the stock cannot refill both players,
the remaining stock cards are set aside and play continues without drawing.

**Winning a deal.** Just before acting, a player may claim to have 31 or
more points in captured cards. A correct claim wins the deal; a wrong claim
loses it. Captured points are hidden during play, as in the real game. If all
cards are played without a claim, the deal is void and the same dealer deals
again. The player who claimed deals the next deal.

**Bura.** A player who holds three trumps at the start of a trick wins the
deal immediately. If both do, the player who would lead wins. (Three aces and
Molodka may be added later.)

**Match.** The first player to win 3 deals wins the match.

## Planned milestones

1. Card and deck model, scoring, and tests (done)
2. Single-card trick comparison (done)
3. Pygame table preview (done)
4. Review fixes: card validation, display labels, separate `gui` package (done)
5. Multi-card trick resolution (done)
6. Dealing, the deal engine, claims, Bura, and full matches (done)
7. Player vs Player in the Pygame interface (done)
8. Algorithmic opponents with three difficulty levels (next)
9. LLM opponent and opponent selector
10. CI and extra features

The separate Durak competition bot is developed on its own.

## How to play

Run `python -m bura` and choose **New 2-player match**. Players share one
screen: a hand-over screen hides the cards while the device is passed.

- Click cards in your hand to raise them, then press **Play**. Play is enabled
  only when the raised cards are a legal lead (1 to 3 cards of one suit) or a
  legal answer (the same number of cards).
- Press **Claim 31** just before acting if you believe you hold 31 points or
  more; you are asked to confirm, because a false claim loses the hand.
- After you answer, a screen shows which cards beat which and who won the trick.
- Escape closes the window. Messages are written to `bura.log`.

## Project layout

```text
src/bura/          game logic (never imports pygame): cards, deck, rules,
                   dealing, game (one hand), match, view, presentation
src/bura/gui/      Pygame user interface (the only code that imports pygame)
tests/             automated tests
```

## Setup and tests

Use Python 3.14 for the course project. From the repository root:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
python -m bura
```

Close the window or press Escape to exit.
