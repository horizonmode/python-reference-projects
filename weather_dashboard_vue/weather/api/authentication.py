from rest_framework.authentication import SessionAuthentication


class CSRFSessionAuthentication(SessionAuthentication):
    """Keep CSRF checks for anonymous writes as well as authenticated sessions."""

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            self.enforce_csrf(request)
        return result
