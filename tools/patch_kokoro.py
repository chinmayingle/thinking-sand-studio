"""Expose Kokoro's per-phoneme durations as a model output named "duration".

The English kokoro-v1.0.onnx release only outputs audio, so kokoro_onnx cannot
give timings. Inside the graph the duration predictor's rounded, clipped integer
durations (one per token, shape [tokens]) feed a CumSum that builds the alignment.
This adds that tensor as a second output; kokoro_onnx then reports exact
per-phoneme start and end times (create_timed). Audio is unchanged.

    python tools/patch_kokoro.py models/kokoro-v1.0.onnx models/kokoro-v1.0-timed.onnx
"""
import sys

import onnx
from onnx import helper, TensorProto


def main(src, dst):
    m = onnx.load(src)
    g = m.graph
    if any(o.name == "duration" for o in g.output):
        onnx.save(m, dst)
        return
    by_out = {o: n for n in g.node for o in n.output}
    rnd = [n for n in g.node if n.op_type == "Round"]
    if len(rnd) != 1:
        raise SystemExit(f"expected one Round node, found {len(rnd)}: unknown model layout")
    consumers = {}
    for n in g.node:
        for i in n.input:
            consumers.setdefault(i, []).append(n)
    # Round -> Clip(min 1) -> Cast(int64) -> Gather(batch 0) -> CumSum
    t = rnd[0].output[0]
    chain = []
    for op in ("Clip", "Cast", "Gather"):
        nxt = [n for n in consumers.get(t, []) if n.op_type == op]
        if not nxt:
            raise SystemExit(f"no {op} after {t}: unknown model layout")
        t = nxt[0].output[0]
        chain.append(op)
    if not any(n.op_type == "CumSum" for n in consumers.get(t, [])):
        raise SystemExit("durations do not feed a CumSum: unknown model layout")
    g.node.append(helper.make_node("Identity", [t], ["duration"], name="expose_duration"))
    g.output.append(helper.make_tensor_value_info("duration", TensorProto.INT64, ["tokens"]))
    onnx.save(m, dst)
    print(f"exposed {t} as 'duration' ({' -> '.join(['Round', *chain])})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
