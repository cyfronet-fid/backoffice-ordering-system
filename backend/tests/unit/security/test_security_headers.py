def test_security_csp_header(client):
    response = client.get("/")

    assert "Content-Security-Policy" in response.headers
    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "script-src 'self' 'unsafe-inline'" in csp
    assert "style-src 'self' 'unsafe-inline'" in csp
    assert "img-src 'self' data:" in csp
    assert "connect-src 'self'" in csp


def test_security_clickjacking(client):
    response = client.get("/")
    assert response.headers["X-Frame-Options"] == "DENY"


def test_security_mime_sniffing(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_security_referrer(client):
    response = client.get("/")
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
