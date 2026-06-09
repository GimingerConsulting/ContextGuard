from pathlib import Path


def test_no_network_runtime_imports():
    root = Path(__file__).resolve().parents[1] / "contextguard"
    forbidden = ("requests", "urllib.request", "http.client", "socket.create_connection")
    for path in root.glob("*.py"):
        text = path.read_text()
        assert not any(item in text for item in forbidden), path
