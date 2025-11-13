import os
from scripts.generate_rtm_report import parse_reports

def test_parse_reports():
    path = os.path.join(os.path.dirname(__file__), ".")
    results, totals = parse_reports(path)
    assert isinstance(results, list)
    assert isinstance(totals, dict)
