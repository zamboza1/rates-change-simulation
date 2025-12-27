import pytest
import os
from src.plots import plot_comparison

def test_plot_comparison_smoke_test(tmp_path):
    """
    Test that plot_comparison runs without crashing and creating a file.
    Using tmp_path fixture to avoid polluting directory.
    """
    curve = {1.0: 4.0, 10.0: 5.0}
    
    # We use a temporary file path
    # tmp_path is a pathlib.Path object
    output_file = tmp_path / "test_plot.png"
    
    try:
        plot_comparison(curve, title="Test", filename=str(output_file))
        assert os.path.exists(output_file)
    except Exception as e:
        pytest.fail(f"Plotting crashed: {e}")

def test_plot_comparison_empty_fail():
    """Verify precondition: empty curve raises Assertion."""
    with pytest.raises(AssertionError):
        plot_comparison({}, filename="irrelevant.png")
