from analysis.data_profiler import profile_dataset
from analysis.statistics import (
    numeric_summary,
    group_analysis,
    calculate_profit_margin,
)
from analysis.anomaly import (
    detect_iqr_anomalies,
)


FILE = "data/sample.csv"


def test_profile():

    result = profile_dataset(FILE)

    assert result["success"] is True
    assert result["rows"] == 10
    assert result["columns"] == 6


def test_numeric_summary():

    result = numeric_summary(FILE)

    assert result["success"] is True

    revenue = result["summary"]["revenue"]

    assert revenue["sum"] == 95000
    assert revenue["mean"] == 9500


def test_group_analysis():

    result = group_analysis(
        FILE,
        "region",
        "revenue",
    )

    assert result["success"] is True


def test_profit_margin():

    result = calculate_profit_margin(
        FILE,
        "revenue",
        "profit",
    )

    assert result["success"] is True


def test_anomaly_detection():

    result = detect_iqr_anomalies(
        FILE,
        "discount",
    )

    assert result["success"] is True