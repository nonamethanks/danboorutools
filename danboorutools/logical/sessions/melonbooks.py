from __future__ import annotations

from typing import TYPE_CHECKING, Any

from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

from danboorutools.logical.sessions import Session

if TYPE_CHECKING:
    from requests import Response


class CypherAdapter(HTTPAdapter):
    """A TransportAdapter that enables weak cyphers."""

    # Adapted from https://stackoverflow.com/a/46186957/11558993
    CIPHERS = (
        "ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:"
        "DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:"
        "!eNULL:!MD5"
    )

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

    def request(self, *args, **kwargs) -> Response:
        cookies = {"AUTH_ADULT": "1"}
        return super().request(*args, cookies=cookies, **kwargs)
