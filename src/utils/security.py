from jose import jwt
import bcrypt
import hashlib
from datetime import datetime, timedelta, timezone

from src.utils.settings import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


def encode_access_token(
    user_id: int,
    email: str,
    role: str,
):
    exp = datetime.now(timezone.utc) + timedelta(hours=24)

    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": exp,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token


def decode_access_token(token: str):

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    return payload


def hash_password(password: str) -> str:

    salt = bcrypt.gensalt()

    return bcrypt.hashpw(
        password.encode("utf-8"),
        salt,
    ).decode("utf-8")


def verify_password(
    password: str,
    hashed_pass: str,
) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_pass.encode("utf-8"),
    )


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def hash_otp(otp: str) -> str:
    return hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()