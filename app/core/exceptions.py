class UrlShortenerError(Exception):
    """Base class for expected application errors."""


class ShortUrlNotFoundError(UrlShortenerError):
    pass


class ShortUrlExpiredError(UrlShortenerError):
    pass


class ShortCodeConflictError(UrlShortenerError):
    pass


class IdSpaceExhaustedError(UrlShortenerError):
    pass
