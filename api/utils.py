from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    """Returns a hashed version of the password for storing in database"""
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    """Verifies if the password given by the user is same as that of stored in the database."""
    return pwd_context.verify(plain_password, hashed_password)
