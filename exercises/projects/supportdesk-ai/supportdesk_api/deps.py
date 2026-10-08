"""The four dependencies the tests replace with fakes (dependency_overrides). Checkpoints C3, C5, C7.

get_llm()         -> .complete(system, messages, tools) -> {"stop_reason": "end_turn" | "tool_use", "content": [blocks]}
                     (block shapes: see exercises/m7/w2/02-tool-loop). Default: a real provider client (checkpoint C10).
get_embedder()    -> .embed(texts) -> one vector per text. Default: a real embedding model or a local one (stretch goal).
get_orders_api()  -> .get_order("ORD-1001") -> {"id", "owner", "status", "eta"} | None   (your mock order service)
get_tracer()      -> .span(name, **attrs): a context manager; the object it yields has .set(**attrs)
"""


def get_llm():
    raise NotImplementedError("C3")


def get_embedder():
    raise NotImplementedError("C2")


def get_orders_api():
    raise NotImplementedError("C5")


def get_tracer():
    raise NotImplementedError("C7")
