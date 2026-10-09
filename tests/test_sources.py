from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from engine import data, sources

ENABLED = [s for s in data.SCHEMES_FILE["schemes"]
           if s.get("enabled", True) and s.get("official_sources")]


@pytest.fixture(autouse=True)
def tmp_hashes(tmp_path, monkeypatch):
    monkeypatch.setattr(sources, "HASH_FILE", tmp_path / "source_hashes.json")


def _const(html):
    return lambda url: html


def test_baseline_unchanged_changed():
    assert ENABLED, "need at least one enabled scheme with a source"
    r1 = sources.check_all(fetcher=_const("<p>Hello</p>"))
    assert {r["status"] for r in r1 if r["url"]} == {"baseline"}
    assert sources.HASH_FILE.exists()
    r2 = sources.check_all(fetcher=_const("<p>  hello </p><script>x=1</script>"))
    assert {r["status"] for r in r2 if r["url"]} == {"unchanged"}
    r3 = sources.check_all(fetcher=_const("<p>Hello, rules updated</p>"))
    assert {r["status"] for r in r3 if r["url"]} == {"changed"}
    r4 = sources.check_all(fetcher=_const("<p>Hello, rules updated</p>"))
    assert {r["status"] for r in r4 if r["url"]} == {"unchanged"}
    row = r1[0]
    assert set(row) == {"scheme_id", "name_en", "url", "status",
                        "checked_at", "stale", "checked_on"}


def test_unreachable():
    def boom(url):
        raise ConnectionError("down")
    res = sources.check_all(fetcher=boom)
    assert res and all(r["status"] == "unreachable" for r in res)


def test_normalise_strips_script_style():
    html = ("<html><head><style>body{color:red}</style>"
            "<script type='x'>alert(1)</script></head>"
            "<body><H1>Scheme  Rules</H1>\n<p>Apply\tnow</p></body></html>")
    out = sources.normalise(html)
    assert out == "scheme rules apply now"
    assert "alert" not in out and "color" not in out


def test_stale_flag():
    schemes = [{"id": "x", "name_en": "X", "enabled": True,
                "official_sources": ["https://example.gov.in"],
                "verification": {"status": "official", "checked_on": "2026-10-09"}},
               {"id": "off", "enabled": False, "official_sources": ["https://o"]}]
    old = sources.check_all(fetcher=_const("a"), today=date(2026, 12, 1), schemes=schemes)
    assert len(old) == 1 and old[0]["stale"] is True
    fresh = sources.check_all(fetcher=_const("a"), today=date(2026, 10, 10), schemes=schemes)
    assert fresh[0]["stale"] is False


def test_does_not_touch_schemes_json():
    before = (sources.config.DATA_DIR / "schemes.json").read_bytes()
    sources.check_all(fetcher=_const("x"))
    assert (sources.config.DATA_DIR / "schemes.json").read_bytes() == before


def test_endpoint(monkeypatch):
    import routes_admin
    monkeypatch.setattr(sources, "fetch", _const("<p>page</p>"))
    app = FastAPI()
    app.include_router(routes_admin.router)
    body = TestClient(app).get("/api/admin/check_sources").json()
    assert body["results"] and all(r["status"] == "baseline"
                                   for r in body["results"] if r["url"])
    assert "never changed automatically" in body["note_en"]
    assert body["note_ta"]
