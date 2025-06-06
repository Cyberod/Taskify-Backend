import random

def generate_otp(length=6) -> str:
    """
    Generate a one-time password (OTP) of a specified length.
    The OTP consists of digits only.
    
        Args:
            length (int): Length of the OTP. Default is 6.
            
        Returns:
            str: Generated OTP as a string.
    """
    
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp