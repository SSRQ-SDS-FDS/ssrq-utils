class I18nValidationError(ValueError):
    """I18n Validation Error."""

    def __init__(self, message: str) -> None:  # noqa: D107
        super().__init__(message)
