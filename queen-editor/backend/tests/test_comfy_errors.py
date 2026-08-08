from backend.services.comfy.errors import ComfyExecutionError, describe


def _status(node_type, message="boom"):
    return {
        "status_str": "error",
        "messages": [
            ["execution_start", {}],
            ["execution_error", {
                "node_id": "41",
                "node_type": node_type,
                "exception_type": "RuntimeError",
                "exception_message": message,
                "current_inputs": {"seed": 7},
                "traceback": ["line 1\n", "line 2\n"],
            }],
        ],
    }


def test_describe_reports_node_and_message():
    text, tb = describe(_status("KSampler"))
    assert "node 41 (KSampler)" in text
    assert "RuntimeError: boom" in text
    assert tb == "line 1\nline 2\n"


def test_no_node_is_treated_differently_from_another():
    # The loader used to be singled out and stopped the whole run on its first failure. Design v2
    # dropped that: whatever node failed, ComfyUI answered, so it is this frame's failure.
    text, _tb = describe(_status("CheckpointLoaderSimple"))
    assert "CheckpointLoaderSimple" in text


def test_status_without_execution_error_is_dumped_raw():
    text, tb = describe({"status_str": "error", "messages": [["execution_cached", {}]]})
    assert "execution_cached" in text          # the raw status, not an invented cause
    assert tb == ""


def test_error_carries_its_parts():
    err = ComfyExecutionError("t", "tb")
    assert (str(err), err.text, err.traceback_text) == ("t", "t", "tb")


def test_the_error_says_the_failure_belongs_to_the_frame():
    # The one flag the domain reads (it must not import this module to ask).
    assert ComfyExecutionError("t", "tb").frame_level is True
