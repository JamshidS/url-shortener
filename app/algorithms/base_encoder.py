import string


class Base62Encoder:
    alphabet = string.ascii_letters + string.digits
    base = len(alphabet)

    def encode(self, number: int) -> str:
        if number < 0:
            raise ValueError("number must be non-negative")
        if number == 0:
            return self.alphabet[0]

        result: list[str] = []
        while number:
            number, remainder = divmod(number, self.base)
            result.append(self.alphabet[remainder])
        return "".join(reversed(result))

    def encode_fixed_length(self, number: int, length: int) -> str:
        if length <= 0:
            raise ValueError("length must be greater than zero")
        if not 0 <= number < self.base**length:
            raise ValueError(f"number does not fit in {length} Base62 characters")
        return self.encode(number).rjust(length, self.alphabet[0])
