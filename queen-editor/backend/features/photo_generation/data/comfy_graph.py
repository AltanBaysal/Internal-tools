"""Reading a ComfyUI graph off disk -- the one way the photo, Krea, Qwen and H3 producers load
theirs (madde 488). Which nodes a graph must hold, and what is written into them, stays with each
producer."""
import json
import os


def load_graph(path, nodes):
    """A fresh copy of the API-format graph at `path`, holding every id in `nodes`.

    Fresh per call: the producer patches the copy, and nothing is ever written back to the shipped
    file. Only a missing file is turned into a sentence; any other read failure is raised as it is.
    """
    try:
        with open(path, encoding="utf-8") as f:
            graph = json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"Grafik yok: {path} — ComfyUI'de "
                           "'Workflow → Export (API)' ile kaydet ve repoya commit'le") from None
    name = os.path.basename(path)
    if "nodes" in graph:
        raise RuntimeError(f"{name} UI formatında — ComfyUI'de "
                           "'Workflow → Export (API)' ile kaydet")
    missing = [node_id for node_id in nodes if node_id not in graph]
    if missing:
        raise RuntimeError(f"{name} grafiğinde {', '.join(missing)} node yok — graf değişmiş, "
                           "node id'lerini güncelle")
    return graph
