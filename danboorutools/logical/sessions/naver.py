from __future__ import annotations

import re

import ring
from bs4 import BeautifulSoup

from danboorutools.logical.sessions import Session


class NaverSession(Session):
    @ring.lru()
    def blog_artist_widget(self, username: str) -> BeautifulSoup:
        headers = {
            "Referer": f"https://blog.naver.com/PostList.naver?blogId={username}&widgetTypeCall=true&directAccess=true",
        }

        params = {
            "blogId": username,
            "listNumVisitor": "10",
            "isVisitorOpen": "false",
            "isBuddyOpen": "false",
            "selectCategoryNo": "",
            "skinId": "0",
            "skinType": "C",
            "isCategoryOpen": "true",
            "isEnglish": "true",
            "listNumComment": "5",
            "areaCode": "11B10101",
            "weatherType": "0",
            "currencySign": "ALL",
            "enableWidgetKeys": "search,rss,counter,menu,profile,category,content,gnb,externalwidget",
            "writingMaterialListType": "1",
            "calType": "",
        }

        response = self.get("https://blog.naver.com/WidgetListAsync.naver", params=params,  headers=headers)
        match = re.search(r"profile : { content : '(.*)' }, challengemastertrack", response.text)
        assert match
        return BeautifulSoup(match.groups()[0], "html5lib")
