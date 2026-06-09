from pathlib import Path

from contextguard.index import refresh_index
from contextguard.task_classifier import classify_task


def test_low_confidence_classification(tmp_path: Path):
    (tmp_path / "app.py").write_text("print('x')\n")
    result = classify_task(tmp_path, "do something unrelated")
    assert result["confidence"] == "low"


def test_filename_classification(tmp_path: Path):
    (tmp_path / "payment_service.py").write_text("class PaymentService: pass\n")
    result = classify_task(tmp_path, "fix payment service")
    assert result["confidence"] in {"medium", "high"}
    assert "payment_service.py" in result["likely_files"]


def test_symbol_classification_from_index(tmp_path: Path):
    path = tmp_path / "service.py"
    path.write_text("class PaymentGateway:\n    pass\n")
    refresh_index(tmp_path)
    result = classify_task(tmp_path, "PaymentGateway bug")
    assert result["confidence"] == "high"
    assert result["likely_symbols"][0]["name"] == "PaymentGateway"
