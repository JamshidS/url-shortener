import pytest

from app.algorithms.base_encoder import Base62Encoder


def test_fixed_length_encoding_is_exactly_seven_characters() -> None:
    encoder = Base62Encoder()

    encoded = encoder.encode_fixed_length(1, 7)

    assert encoded == "aaaaaab"
    assert len(encoded) == 7


def test_fixed_length_encoding_rejects_overflow() -> None:
    encoder = Base62Encoder()

    with pytest.raises(ValueError):
        encoder.encode_fixed_length(62**7, 7)
