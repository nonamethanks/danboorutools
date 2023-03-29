from __future__ import annotations

from danboorutools.logical.sessions import Session


class DlsiteSession(Session):
    def cien_id_from_circle_id(self, circle_id: str) -> int:
        data = self.get_json(f"https://media.ci-en.jp/dlsite/lookup/{circle_id}.json")
        return data[0]["id"]
