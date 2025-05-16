from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    """
    A utility class for hashing passwords and verifying them.
    """ 
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password (str): The plain password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)