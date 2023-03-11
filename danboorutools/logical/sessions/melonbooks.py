from typing import Any

from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import DEFAULT_CIPHERS, create_urllib3_context

from danboorutools.logical.sessions import Session


class CypherAdapter(HTTPAdapter):
    """A TransportAdapter that enables weak cyphers."""

    # Adapted from https://stackoverflow.com/a/46186957/11558993
    CIPHERS = DEFAULT_CIPHERS + "HIGH:!DH:!aNULL"

    def init_poolmanager(self, *args, **kwargs) -> Any:  # noqa: ANN401
        """Initialize a urllib3 PoolManager."""
        context = create_urllib3_context(ciphers=self.CIPHERS)
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs) -> Any:  # noqa: ANN401
        """Return urllib3 ProxyManager for the given proxy."""
        context = create_urllib3_context(ciphers=self.CIPHERS)
        kwargs["ssl_context"] = context
        return super().proxy_manager_for(*args, **kwargs)


class MelonbooksSession(Session):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        cypher_adapter = CypherAdapter()
        self.mount("http://www.melonbooks.co.jp", cypher_adapter)
        self.mount("https://www.melonbooks.co.jp", cypher_adapter)
