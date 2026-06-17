import pytest
from src.etl.normaliser import normalize_ticker, normalize_year

# 15 Test Cases for Ticker Normalization
@pytest.mark.parametrize("input_ticker, expected", [
    (" tcs ", "TCS"),
    ("HdfcBank", "HDFCBANK"),
    ("infy", "INFY"),
    ("abb", "ABB"),
    ("wipro", "WIPRO"),
    ("  reliance ", "RELIANCE"),
    ("sbin", "SBIN"),
    ("TRENT", "TRENT"),
    ("zomato", "ZOMATO"),
    ("Titan", "TITAN"),
    ("cipla", "CIPLA"),
    ("maruti", "MARUTI"),
    ("axisbank", "AXISBANK"),
    (None, ""),
    (float('nan'), ""),
])
def test_normalize_ticker(input_ticker, expected):
    assert normalize_ticker(input_ticker) == expected


# 20 Test Cases for Year/Date Normalization
@pytest.mark.parametrize("input_year, expected", [
    ("Mar 2024", "2024-03"),
    ("Mar-24", "2024-03"),
    ("2015", "2015-03"),
    ("Dec 2012", "2012-12"),
    ("Sep-20", "2020-09"),
    ("Mar 2013", "2013-03"),
    ("Mar 2014", "2014-03"),
    ("Mar 2016", "2016-03"),
    ("Mar 2017", "2017-03"),
    ("Mar 2018", "2018-03"),
    ("Mar 2019", "2019-03"),
    ("Mar 2020", "2020-03"),
    ("Mar 2021", "2021-03"),
    ("Mar 2022", "2022-03"),
    ("Mar 2023", "2023-03"),
    ("Sep 2024", "2024-09"),
    ("Dec-15", "2015-12"),
    ("Jun-18", "2018-06"),
    (None, ""),
    (float('nan'), ""),
])
def test_normalize_year(input_year, expected):
    assert normalize_year(input_year) == expected