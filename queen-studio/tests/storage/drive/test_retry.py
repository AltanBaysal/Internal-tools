from datetime import timedelta

import pytest

from core.clock.clock import ManualClock
from core.storage.drive.api import DriveError, DriveLost
from core.storage.drive.retry import (
    BUDGET,
    Backoff,
    Conflict,
    Missing,
    refusal,
    resumed,
    retryable,
)
from core.storage.port import Rejected, Unconfirmed
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


# -- a resumable upload's chunk (the m534 spec, Yükleme) ------------------------------------------


def test_a_cut_chunk_is_followed_by_asking_drive_where_the_upload_stands() -> None:
    clock = ManualClock(T0)
    made: list[str] = []

    def send() -> int:
        made.append("send")
        raise DriveLost("Connection reset by peer")

    def status() -> int:
        made.append("status")
        return 8

    assert resumed(Backoff(clock, jitter=lambda: 0), send, status) == 8
    # Never sent twice blind: the answer says where to go on from.
    assert made == ["send", "status"]
    assert clock.now() == T0 + timedelta(seconds=1)


def test_a_chunk_drive_refused_ends_rejected_one_that_may_have_arrived_unconfirmed() -> None:
    def refused() -> int:
        raise DriveError(429, "rateLimitExceeded", "Rate Limit Exceeded")

    def lost() -> int:
        raise DriveLost("The read operation timed out")

    def status() -> int:
        raise DriveError(503, "transientError", "Transient failure")

    with pytest.raises(Rejected, match="Transient"):
        resumed(Backoff(ManualClock(T0)), refused, status)
    with pytest.raises(Unconfirmed, match="Transient"):
        resumed(Backoff(ManualClock(T0)), lost, status)


def test_a_session_drive_no_longer_has_is_missing() -> None:
    def gone() -> int:
        raise DriveError(404, "notFound", "The upload session is not found.")

    with pytest.raises(Missing):
        resumed(Backoff(ManualClock(T0)), gone, gone)


def test_the_waits_of_a_stalled_upload_share_one_budget() -> None:
    # The caller hands in its Backoff: rounds without progress spend one budget, not one each.
    clock = ManualClock(T0)
    stall = Backoff(clock, jitter=lambda: 0)

    def lost() -> int:
        raise DriveLost("reset")

    def status() -> int:
        return 0

    for _ in range(5):  # 1 + 2 + 4 + 8 + 16 s
        resumed(stall, lost, status)
    with pytest.raises(Unconfirmed):
        resumed(stall, lost, status)


def test_a_last_chunk_meeting_a_file_made_meanwhile_is_a_conflict() -> None:
    # Another upload of the same ref finished first: compared by the caller, as at a start.
    def made() -> int:
        raise DriveError(409, "duplicate", "A file already exists with the provided ID.")

    with pytest.raises(Conflict):
        resumed(Backoff(ManualClock(T0)), made, made)
