import json

import pytest

from tool_loop import Tool, TooManySteps, run_agent, run_tool_call


def get_order(ctx, order_id):
    orders = {"A1": {"id": "A1", "status": "shipped", "owner": "u1"}, "B2": {"id": "B2", "status": "paid", "owner": "u2"}}
    order = orders.get(order_id)
    if order is None or order["owner"] != ctx["user_id"]:
        raise LookupError("order not found")         # also used for 'not yours': do not reveal that it exists
    return order


def echo(ctx, text):
    return text


ORDER_TOOL = Tool("get_order", "Look up one of the customer's orders", ["order_id"], get_order)
ECHO_TOOL = Tool("echo", "Repeat text", ["text"], echo)
TOOLS = {t.name: t for t in (ORDER_TOOL, ECHO_TOOL)}
CTX = {"user_id": "u1"}


def call(name, input, id="toolu_1"):
    return {"type": "tool_use", "id": id, "name": name, "input": input}


def test_schema():
    assert ORDER_TOOL.schema() == {
        "name": "get_order",
        "description": "Look up one of the customer's orders",
        "input_schema": {"type": "object", "required": ["order_id"]},
    }


def test_successful_call_returns_json_text_without_is_error():
    block = run_tool_call(TOOLS, call("get_order", {"order_id": "A1"}), CTX)
    assert block["type"] == "tool_result" and block["tool_use_id"] == "toolu_1"
    assert json.loads(block["content"])["status"] == "shipped"
    assert "is_error" not in block


def test_string_results_stay_strings():
    assert run_tool_call(TOOLS, call("echo", {"text": "hi"}), CTX)["content"] == "hi"


def test_unknown_tool():
    block = run_tool_call(TOOLS, call("delete_everything", {}), CTX)
    assert block["is_error"] is True and block["content"] == "unknown tool: delete_everything"


def test_missing_required_input():
    block = run_tool_call(TOOLS, call("get_order", {}), CTX)
    assert block["is_error"] is True and block["content"] == "missing required input: order_id"


def test_missing_inputs_are_listed_sorted():
    tool = Tool("t", "d", ["b", "a"], lambda ctx, a, b: "x")
    block = run_tool_call({"t": tool}, call("t", {}), CTX)
    assert block["content"] == "missing required input: a, b"


def test_tool_exceptions_become_error_results():
    block = run_tool_call(TOOLS, call("get_order", {"order_id": "ZZZ"}), CTX)
    assert block["is_error"] is True and block["content"] == "tool failed: LookupError: order not found"


def test_the_app_context_decides_what_the_user_may_see():
    # B2 belongs to u2; the model cannot change who the user is
    block = run_tool_call(TOOLS, call("get_order", {"order_id": "B2"}), CTX)
    assert block["is_error"] is True and "not found" in block["content"]
    assert "is_error" not in run_tool_call(TOOLS, call("get_order", {"order_id": "B2"}), {"user_id": "u2"})


def test_a_model_supplied_user_id_is_ignored_as_an_argument():
    # fn has no user_id parameter: passing one is a TypeError → an error result, not a data leak
    block = run_tool_call(TOOLS, call("get_order", {"order_id": "B2", "user_id": "u2"}), CTX)
    assert block["is_error"] is True


class FakeLLM:
    def __init__(self, *replies):
        self.replies = list(replies)
        self.seen = []

    def __call__(self, messages):
        self.seen.append(messages)
        return self.replies.pop(0)


def text(t, stop="end_turn"):
    return {"stop_reason": stop, "content": [{"type": "text", "text": t}]}


def test_no_tools_needed():
    llm = FakeLLM(text("Hello!"))
    out = run_agent(llm, [ORDER_TOOL], "Hi", CTX)
    assert out["text"] == "Hello!" and out["steps"] == 1
    assert out["messages"] == [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": [{"type": "text", "text": "Hello!"}]},
    ]


def test_one_tool_round_trip():
    llm = FakeLLM(
        {"stop_reason": "tool_use", "content": [{"type": "text", "text": "Let me check."}, call("get_order", {"order_id": "A1"})]},
        text("Your order has shipped."),
    )
    out = run_agent(llm, [ORDER_TOOL], "Where is order A1?", CTX)
    assert out["text"] == "Your order has shipped." and out["steps"] == 2
    roles = [m["role"] for m in out["messages"]]
    assert roles == ["user", "assistant", "user", "assistant"]
    results = out["messages"][2]["content"]
    assert len(results) == 1 and results[0]["tool_use_id"] == "toolu_1"
    assert json.loads(results[0]["content"])["status"] == "shipped"


def test_parallel_calls_come_back_in_one_user_message_in_order():
    llm = FakeLLM(
        {"stop_reason": "tool_use", "content": [call("echo", {"text": "one"}, "t1"), call("echo", {"text": "two"}, "t2")]},
        text("done"),
    )
    out = run_agent(llm, [ECHO_TOOL], "go", CTX)
    results = out["messages"][2]["content"]
    assert [r["tool_use_id"] for r in results] == ["t1", "t2"]
    assert [r["content"] for r in results] == ["one", "two"]
    assert len(out["messages"]) == 4                       # exactly ONE user message for both results


def test_a_failing_tool_does_not_stop_the_loop_and_the_model_sees_the_error():
    llm = FakeLLM(
        {"stop_reason": "tool_use", "content": [call("get_order", {"order_id": "ZZZ"})]},
        text("Sorry, I could not find that order."),
    )
    out = run_agent(llm, [ORDER_TOOL], "order ZZZ?", CTX)
    assert out["messages"][2]["content"][0]["is_error"] is True
    assert out["text"].startswith("Sorry")


def test_multi_step_chain():
    llm = FakeLLM(
        {"stop_reason": "tool_use", "content": [call("echo", {"text": "a"}, "t1")]},
        {"stop_reason": "tool_use", "content": [call("echo", {"text": "b"}, "t2")]},
        text("finished"),
    )
    out = run_agent(llm, [ECHO_TOOL], "go", CTX)
    assert out["steps"] == 3 and len(out["messages"]) == 6


def test_the_model_gets_a_copy_of_the_history():
    llm = FakeLLM({"stop_reason": "tool_use", "content": [call("echo", {"text": "a"})]}, text("ok"))
    out = run_agent(llm, [ECHO_TOOL], "go", CTX)
    assert len(llm.seen[0]) == 1          # not rewritten by later appends
    assert len(llm.seen[1]) == 3
    assert out["steps"] == 2


def test_runaway_loop_is_stopped():
    llm = FakeLLM(*[{"stop_reason": "tool_use", "content": [call("echo", {"text": "again"}, f"t{i}")]} for i in range(10)])
    with pytest.raises(TooManySteps):
        run_agent(llm, [ECHO_TOOL], "go", CTX, max_steps=3)
    assert len(llm.seen) == 3


def test_max_tokens_or_refusal_ends_the_loop_with_the_text_so_far():
    llm = FakeLLM(text("Partial ans", stop="max_tokens"))
    out = run_agent(llm, [ECHO_TOOL], "go", CTX)
    assert out["text"] == "Partial ans" and out["steps"] == 1
