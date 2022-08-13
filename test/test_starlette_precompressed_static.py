from pathlib import Path
from typing import List

from pytest import raises
from starlette.exceptions import HTTPException
from starlette.testclient import TestClient

from starlette_precompressed_static import PreCompressedStaticFiles


def _compare_accepted_encoding_parsing(header: str, result: List[str]):
    assert (
        PreCompressedStaticFiles._PreCompressedStaticFiles__get_accepted_encodings(  # type:ignore
            header
        )
        == result
    )


def test_accepted_encoding_parsing():
    _compare_accepted_encoding_parsing("br", ["br"])
    _compare_accepted_encoding_parsing("br, gzip", ["br", "gzip"])
    _compare_accepted_encoding_parsing("br,gzip", ["br", "gzip"])
    _compare_accepted_encoding_parsing("br, gzip, *;q=0", ["br", "gzip"])
    _compare_accepted_encoding_parsing("br;q=0, gzip", ["gzip"])
    _compare_accepted_encoding_parsing("br;q=0.2, gzip;q=0.3", ["br", "gzip"])
    _compare_accepted_encoding_parsing("gzip, deflate, br", ["gzip", "deflate", "br"])


def test_html_mode():
    with raises(NotImplementedError):
        PreCompressedStaticFiles(directory=Path("./test/resources"), html=True)


def test_uncompressed_css():

    app = PreCompressedStaticFiles(directory=Path("./test/resources"))
    client = TestClient(app)
    response = client.get("/test.css", headers={"Accept-Encoding": ""})
    assert response.status_code == 200
    assert response.headers["Content-Length"] == "379"
    assert response.headers["Content-Type"] == "text/css; charset=utf-8"
    assert "Accept-Encoding" in response.headers["Vary"]
    assert "Content-Encoding" not in response.headers


def test_brotli_encoded_css():

    app = PreCompressedStaticFiles(directory=Path("./test/resources"))
    client = TestClient(app)
    response = client.get("/test.css", headers={"Accept-Encoding": "br"})
    assert response.status_code == 200
    assert response.headers["Content-Length"] == "40"
    assert response.headers["Content-Type"] == "text/css; charset=utf-8"
    assert "Accept-Encoding" in response.headers["Vary"]
    assert response.headers["Content-Encoding"] == "br"


def test_gzipped_css():

    app = PreCompressedStaticFiles(directory=Path("./test/resources"))
    client = TestClient(app)
    response = client.get("/test.css", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers["Content-Length"] == "68"
    assert response.headers["Content-Type"] == "text/css; charset=utf-8"
    assert "Accept-Encoding" in response.headers["Vary"]
    assert response.headers["Content-Encoding"] == "gzip"


def test_uncompressed_js():

    app = PreCompressedStaticFiles(directory=Path("./test/resources"))
    client = TestClient(app)
    response = client.get("/test.js", headers={"Accept-Encoding": ""})
    assert response.status_code == 200
    assert response.headers["Content-Length"] == "522"
    assert response.headers["Content-Type"] == "application/javascript"
    assert "Accept-Encoding" in response.headers["Vary"]
    assert "Content-Encoding" not in response.headers


def test_brotli_encoded_js():

    app = PreCompressedStaticFiles(directory=Path("./test/resources"))
    client = TestClient(app)
    response = client.get("/test.js", headers={"Accept-Encoding": "br"})
    assert response.status_code == 200
    assert response.headers["Content-Length"] == "32"
    assert response.headers["Content-Type"] == "application/javascript"
    assert "Accept-Encoding" in response.headers["Vary"]
    assert response.headers["Content-Encoding"] == "br"


def test_gzipped_js():

    app = PreCompressedStaticFiles(directory=Path("./test/resources"))
    client = TestClient(app)
    response = client.get("/test.js", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers["Content-Length"] == "55"
    assert response.headers["Content-Type"] == "application/javascript"
    assert "Accept-Encoding" in response.headers["Vary"]
    assert response.headers["Content-Encoding"] == "gzip"


def test_accept_both_brotli_and_gz():
    app = PreCompressedStaticFiles(directory=Path("./test/resources"))
    client = TestClient(app)
    response = client.get("/test.css", headers={"Accept-Encoding": "gzip, br"})
    assert response.status_code == 200
    assert response.headers["Content-Length"] == "40"
    assert response.headers["Content-Type"] == "text/css; charset=utf-8"
    assert "Accept-Encoding" in response.headers["Vary"]
    assert response.headers["Content-Encoding"] == "br"


def test_disable_brotli():
    app = PreCompressedStaticFiles(directory=Path("./test/resources"), brotli=False)
    client = TestClient(app)
    response = client.get("/test.js", headers={"Accept-Encoding": "br, gzip"})
    assert response.status_code == 200
    assert response.headers["Content-Length"] == "55"
    assert response.headers["Content-Type"] == "application/javascript"
    assert "Accept-Encoding" in response.headers["Vary"]
    assert response.headers["Content-Encoding"] == "gzip"


def test_disable_gzip():
    app = PreCompressedStaticFiles(directory=Path("./test/resources"), gzip=False)
    client = TestClient(app)
    response = client.get("/test.js", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers["Content-Length"] == "522"
    assert response.headers["Content-Type"] == "application/javascript"
    assert "Accept-Encoding" in response.headers["Vary"]
    assert "Content-Encoding" not in response.headers


def test_missing_compressed_version_gzip():
    app = PreCompressedStaticFiles(directory=Path("./test/resources"))
    client = TestClient(app)
    response = client.get("/forgotten.css", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers["Content-Length"] == "379"
    assert response.headers["Content-Type"] == "text/css; charset=utf-8"
    assert "Accept-Encoding" in response.headers["Vary"]
    assert "Content-Encoding" not in response.headers


def test_missing_compressed_version_brotli():
    app = PreCompressedStaticFiles(directory=Path("./test/resources"))
    client = TestClient(app)
    response = client.get("/forgotten.css", headers={"Accept-Encoding": "br"})
    assert response.status_code == 200
    assert response.headers["Content-Length"] == "379"
    assert response.headers["Content-Type"] == "text/css; charset=utf-8"
    assert "Accept-Encoding" in response.headers["Vary"]
    assert "Content-Encoding" not in response.headers


def test_missing_file():
    app = PreCompressedStaticFiles(directory=Path("./test/resources"))
    client = TestClient(app)
    with raises(HTTPException) as error:
        client.get("/not-there.css", headers={"Accept-Encoding": "br"})
    assert error.value.status_code == 404


def test_wrong_method():
    app = PreCompressedStaticFiles(directory=Path("./test/resources"))
    client = TestClient(app)
    with raises(HTTPException) as error:
        client.delete("/test.js", headers={"Accept-Encoding": "br"})
    assert error.value.status_code == 405


def test_missing_compressed_version_wrong_method():
    app = PreCompressedStaticFiles(directory=Path("./test/resources"))
    client = TestClient(app)
    with raises(HTTPException) as error:
        client.post("/forgotten.css", headers={"Accept-Encoding": "br"})
    assert error.value.status_code == 405
