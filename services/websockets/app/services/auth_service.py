from jose import JWTError, jwt

from app.core.config import settings


class AuthError(Exception):
    pass


class AuthService:
    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except JWTError as exc:
            raise AuthError("Invalid token") from exc

    def get_user_id(self, token: str) -> str:
        payload = self.decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthError("Token does not contain subject")
        return user_id