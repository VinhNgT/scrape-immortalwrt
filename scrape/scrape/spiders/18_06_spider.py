# This spider is used to scrape the 18.06-SNAPSHOT target files structure from the ImmortalWRT website

from scrapy import Spider, Request


class _18_06_Spider(Spider):
    name = "18_06_Spider"
    start_urls = ["https://downloads.immortalwrt.org/releases/18.06-SNAPSHOT/targets/"]

    custom_settings = {
        # "DOWNLOAD_DELAY": 1,
        "AUTOTHROTTLE_ENABLED": True,
    }

    def parse(self, response):
        isSupplementaryMeta = response.meta.get("isSupplementary")
        isSupplementaryMeta = (
            False if isSupplementaryMeta is None else isSupplementaryMeta
        )

        # print("################################################### parse start")

        tables = response.xpath("//table")

        for table_id, table in enumerate(tables):
            sublinks = table.xpath(".//a")

            for link in sublinks:
                fullLink = response.request.url + link.xpath("./@href").get()
                sha256sum = link.xpath("./ancestor::*[2]/td[@class='sh']/text()").get()
                size = link.xpath("./ancestor::*[2]/td[@class='s']/text()").get()
                date = link.xpath("./ancestor::*[2]/td[@class='d']/text()").get()

                linkInfo = {
                    "link": fullLink,
                    "sha256sum": self.normalize_null(sha256sum),
                    "size": self.normalize_null(size),
                    "date": date,
                    "isFile": fullLink[-1] != "/",
                    "isSupplementary": (table_id >= 1) or isSupplementaryMeta,
                }

                yield linkInfo

                if not linkInfo["isFile"]:
                    yield Request(
                        fullLink,
                        callback=self.parse,
                        meta={
                            "isSupplementary": linkInfo["isSupplementary"],
                        },
                    )

                # break

        # print("################################################### parse end")

    def normalize_null(self, input: str):
        if input == "-":
            return None

        return input
