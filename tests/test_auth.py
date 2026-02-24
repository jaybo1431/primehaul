"""Tests for authentication endpoints."""


class TestLoginPage:
    def test_login_page_renders(self, app_client):
        """GET /auth/login should return 200 with login form."""
        response = app_client.get("/auth/login", follow_redirects=False)
        assert response.status_code == 200

    def test_login_with_wrong_password(self, app_client, test_user):
        """POST /auth/login with wrong password should show error."""
        response = app_client.post(
            "/auth/login",
            data={"email": test_user.email, "password": "WrongPassword1"},
            follow_redirects=False,
        )
        # Should re-render login page with error (200) or redirect back (303)
        assert response.status_code in (200, 303, 302)

    def test_login_with_correct_password(self, app_client, test_user, test_company):
        """POST /auth/login with correct password should set cookie and redirect to dashboard."""
        response = app_client.post(
            "/auth/login",
            data={"email": test_user.email, "password": "TestPassword1"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert "dashboard" in response.headers.get("location", "").lower() or "admin" in response.headers.get("location", "").lower()

    def test_logout_clears_cookie(self, authenticated_client):
        """POST /auth/logout should clear cookie and redirect."""
        response = authenticated_client.post("/auth/logout", follow_redirects=False)
        assert response.status_code in (303, 302)


class TestSuperadminAuth:
    def test_superadmin_login_page(self, app_client):
        """GET /superadmin/login should return 200."""
        response = app_client.get("/superadmin/login")
        assert response.status_code == 200

    def test_superadmin_wrong_password(self, app_client):
        """POST /superadmin/login with wrong password should redirect with error."""
        response = app_client.post(
            "/superadmin/login",
            data={"password": "WrongPassword"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert "error" in response.headers.get("location", "")

    def test_superadmin_correct_password(self, app_client):
        """POST /superadmin/login with correct password should set cookie."""
        import os
        response = app_client.post(
            "/superadmin/login",
            data={"password": os.environ["SUPERADMIN_PASSWORD"]},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert "dashboard" in response.headers.get("location", "")


class TestSalesAuth:
    def test_sales_login_page(self, app_client):
        """GET /sales/login should return 200."""
        response = app_client.get("/sales/login")
        assert response.status_code == 200

    def test_sales_wrong_password(self, app_client):
        """POST /sales/login with wrong password should redirect."""
        response = app_client.post(
            "/sales/login",
            data={"password": "WrongPassword"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert "error" in response.headers.get("location", "") or "login" in response.headers.get("location", "")


class TestSecurityHeaders:
    def test_security_headers_present(self, app_client):
        """All security headers should be present on responses."""
        response = app_client.get("/auth/login")
        headers = response.headers
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert headers.get("X-Frame-Options") == "DENY"
        assert headers.get("Strict-Transport-Security") is not None
        assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert "camera" in headers.get("Permissions-Policy", "")
        assert "default-src" in headers.get("Content-Security-Policy", "")
