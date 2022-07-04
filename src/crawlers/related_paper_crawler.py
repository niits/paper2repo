import requests
import time
import re
from typing import List
import parsel
from urllib.parse import urljoin

from ..exceptions import CrawlingException

class RelatedPaperCrawler:
    def __init__(self, base_url: str = "https://scholar.google.com/scholar"):
        self.base_url = base_url

        self._make_session()

    def refresh(self):
        self.session.close()
        del self.session
        time.sleep(2)
        self._make_session()

    def find_related_papers(self, paper_title: str) -> List[str]:
        url = self._get_related_paper_url(paper_title)
        return self._get_related_papers(url)

    def _make_session(self):
        self.session = requests.Session()
        self.session.get(self.base_url)

    def _get_related_paper_url(self, paper_title: str) -> str:
        paper_title = self._normalize_paper_title(paper_title)
        res = self.session.get(
            urljoin(
                self.base_url, f"/scholar?hl=en&as_sdt=0%2C5&q={paper_title}&btnG="
            ),
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Linux"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "x-client-data": "CK21yQEIh7bJAQimtskBCKmdygEI0+bKAQiTocsBCNvvywEIhLTMAQiFtMwBCJa2zAEI67nMAQi5uswBGKupygE=",
            },
        )

        selector = parsel.Selector(text=res.text)
        result_sections = selector.css("#gs_res_ccl_mid > div > div.gs_ri")
        if len(result_sections) == 0:
            raise CrawlingException()

        section = result_sections[0]

        tags = [a_tag for a_tag in section.css("a") if self.match_content(a_tag)]

        if len(tags) == 0:
            raise CrawlingException()

        tag = tags[0]
        return tag.attrib["href"]

    def _get_related_papers(self, target_url: str) -> List[str]:
        res = self.session.get(urljoin(self.base_url, target_url))

        selector = parsel.Selector(text=res.text)

        return selector.css("#gs_res_ccl_mid > div > div.gs_ri > h3 > a::text").getall()

    def _normalize_paper_title(self, paper_title: str) -> str:
        return re.sub(r"[^A-Za-z0-9]+", paper_title.strip(), "+")

    def match_content(self, a_tag, content: str = "Related articles"):
        text = a_tag.css("::text").get()
        return text and text.strip() == content
