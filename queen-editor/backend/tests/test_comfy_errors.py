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
    text, tb, infra = describe(_status("KSampler"))
    assert "node 41 (KSampler)" in text
    assert "RuntimeError: boom" in text
    assert tb == "line 1\nline 2\n"
    assert infra is False


def test_loader_node_is_infra():
    _text, _tb, infra = describe(_status("CheckpointLoaderSimple"))
    assert infra is True


def test_loader_is_recognised_mid_name():
    # A real node in our graph: the name ends in "(rgthree)", not in "loader".
    _text, _tb, infra = describe(_status("Power Lora Loader (rgthree)"))
    assert infra is True


def test_status_without_execution_error_is_dumped_raw():
    text, tb, infra = describe({"status_str": "error", "messages": [["execution_cached", {}]]})
    assert "execution_cached" in text          # the raw status, not an invented cause
    assert (tb, infra) == ("", False)


def test_error_carries_its_parts():
    err = ComfyExecutionError("t", "tb", True)
    assert (str(err), err.text, err.traceback_text, err.infra) == ("t", "t", "tb", True)
