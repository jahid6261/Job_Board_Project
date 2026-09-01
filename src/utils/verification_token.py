import secrets


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)




def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"