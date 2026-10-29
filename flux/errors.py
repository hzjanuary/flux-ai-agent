"""Public, content-free failure codes. Never forward upstream exception text."""


class FluxError(Exception):
    pass


class ConfigError(FluxError):
    pass


class Denied(FluxError):
    pass


class InvalidCall(FluxError):
    pass


class BudgetExceeded(FluxError):
    pass


class ProviderError(FluxError):
    def __init__(self, code: str, retryable: bool = False):
        self.code = code
        self.retryable = retryable
        super().__init__(code)
