import string

from fastapi import Request


class Base62Encoder:

    def __init__(self):
        self.characters = string.ascii_letters + string.digits
        self.base = 62
    
    def encode(self, num: int) -> str:
        if num == 0:
            return self.characters[0]

        result = []
        while num > 0:
            remainder = num % self.base
            result.append(self.characters[remainder])
            num //= self.base
        
        return ''.join(reversed(result))

    def encode_fixed_length(self, num: int, length: int) -> str:
        """Encode a number into an exact number of Base62 characters."""
        if length <= 0:
            raise ValueError("length must be greater than zero")

        code_space = self.base ** length
        if not 0 <= num < code_space:
            raise ValueError(f"number does not fit in {length} Base62 characters")

        encoded = self.encode(num)
        return encoded.rjust(length, self.characters[0])
    

def get_base62_encoder(request: Request) -> Base62Encoder:
    return request.app.state.base62_encoder
