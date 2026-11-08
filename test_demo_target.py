import sqlite3
import pytest
import demo_target

class FakeCursor:
    def __init__(self, result=None, exception=None):
        self.result = result
        self.exception = exception
        self.last_query = None
        self.last_params = None

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params
        if self.exception:
            raise self.exception

    def fetchone(self):
        return self.result

class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.closed = False

    def cursor(self):
        return self._cursor

    def close(self):
        self.closed = True

@pytest.fixture
def fake_db(monkeypatch):
    def _create_fake_db(result=None, exception=None):
        cursor = FakeCursor(result=result, exception=exception)
        conn = FakeConnection(cursor)
        monkeypatch.setattr(demo_target.sqlite3, "connect", lambda *args, **kwargs: conn)
        return conn, cursor
    return _create_fake_db

def test_get_user_data_returns_row(fake_db):
    expected = (1, "Alice")
    conn, cursor = fake_db(result=expected)
    result = demo_target.get_user_data(1)
    assert result == expected
    assert cursor.last_params == (1,)
    assert conn.closed is True

def test_get_user_data_returns_none_when_not_found(fake_db):
    conn, cursor = fake_db(result=None)
    result = demo_target.get_user_data(999)
    assert result is None
    assert cursor.last_params == (999,)
    assert conn.closed is True

def test_get_user_data_passes_user_id_tuple(fake_db):
    conn, cursor = fake_db(result=(2, "Bob"))
    demo_target.get_user_data(2)
    assert cursor.last_params == (2,)

def test_get_user_data_accepts_string_id(fake_db):
    conn, cursor = fake_db(result=("a", "Alpha"))
    result = demo_target.get_user_data("a")
    assert result == ("a", "Alpha")
    assert cursor.last_params == ("a",)
    assert conn.closed is True

def test_get_user_data_closes_connection_on_exception(fake_db):
    conn, cursor = fake_db(exception=RuntimeError("database error"))
    with pytest.raises(RuntimeError, match="database error"):
        demo_target.get_user_data(1)
    assert conn.closed is True

def test_calculate_rate_valid_integers():
    assert demo_target.calculate_rate(100, 10) == pytest.approx(10.0)

def test_calculate_rate_valid_floats():
    assert demo_target.calculate_rate(5.5, 2.0) == pytest.approx(2.75)

def test_calculate_rate_zero_time_returns_zero():
    assert demo_target.calculate_rate(100, 0) == 0.0

def test_calculate_rate_zero_requests_returns_zero():
    assert demo_target.calculate_rate(0, 10) == 0.0

def test_calculate_rate_zero_requests_and_zero_time_returns_zero():
    assert demo_target.calculate_rate(0, 0) == 0.0

def test_calculate_rate_negative_values():
    assert demo_target.calculate_rate(-100, 10) == pytest.approx(-10.0)

def test_calculate_rate_large_values():
    result = demo_target.calculate_rate(10**18, 10**9)
    assert result == pytest.approx(10**9)