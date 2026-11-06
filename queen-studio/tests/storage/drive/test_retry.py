from datetime import timedelta

import pytest

from core.clock.clock import ManualClock
from core.storage.drive.api import DriveError, DriveLost
from core.storage.drive.retry import BUDGET, Backoff, refusal, retryable
from tests.storage.contract import T0


def test_the_waits_double_up_to_the_cap_within_the_budget() -> None:
    clock = ManualClock(T0)
    backoff = Backoff(clock, jitter=lambda: 0.5)

    waited: list[float] = []
    while backoff.wait():
        waited.append((clock.now() - T0).total_seconds())

    # 1, 2, 4, 8 and 16 s, each with its jitter; 32 more would pass the 60 s budget.
    assert waited == [1.5, 4.0, 8.5, 17.0, 33.5]


def test_time_spent_in_the_calls_counts_against_the_budget() -> None:
    # A hung call holds its timeout; the budget is the clock's, so it ends sooner.
    clock = ManualClock(T0)
    backoff = Backoff(clock, jitter=lambda: 0)

    clock.sleep(30)
    assert backoff.wait()
    clock.sleep(30)

    assert not backoff.wait()
    assert clock.now() == T0 + timedelta(seconds=61)


def test_the_budget_is_about_a_minute() -> None:
    assert BUDGET == 60


@pytest.mark.parametrize(
    ("error", "again", "refused"),
    [
        (DriveError(429, "rateLimitExceeded", "Rate Limit Exceeded"), True, True),
        (DriveError(403, "userRateLimitExceeded", "User rate limit exceeded."), True, True),
        (DriveError(503, "transientError", "Transient failure"), True, False),
        (DriveError(500, "backendError", "Backend Error"), True, False),
        (DriveLost("timed out"), True, False),
        (DriveError(403, "appNotAuthorizedToChild", "The user has not granted..."), False, False),
        (DriveError(404, "notFound", "File not found: x."), False, False),
        (DriveError(400, "badRequest", "The provided file ID is not usable."), False, False),
    ],
)
def test_which_errors_are_tried_again(
    error: DriveError | DriveLost, again: bool, refused: bool
) -> None:
    # Step 4: 429, 403 userRateLimitExceeded and 503 transientError back off (528 saw the 503s);
    # a refusal for the rate is one where Drive did nothing.
    assert retryable(error) is again
    assert refusal(error) is refused
