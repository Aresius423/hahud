import requests
from lxml import html
from lxml import etree
from lxml.etree import tostring

from cache import loadToCache
from datamodels import car

header = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0",
}


def page(num, base):
    return base + "/page" + str(num)


def fetch_results_from_query(query):
    initReq = requests.get(query.url, headers=header)
    initTree = html.fromstring(initReq.content)

    try:
        num_of_pages = int(
            initTree.xpath('//link[@rel="last"]/@href')[0].split("page")[1]
        )
    except IndexError:
        num_of_pages = 1

    results = []

    for pagenum in range(1, num_of_pages + 1):
        print(f"\rProcessing page {str(pagenum)} out of {str(num_of_pages)} for query {query.name}", end="")
        request = requests.get(page(pagenum, query.url))
        tree = html.fromstring(request.content)
        listings = tree.xpath('.//div[contains(@class, "row talalati-sor")]')

        for listing in listings:
            kepsor = listing.find('.//div[@class="talalatisor-kep"]')
            adatsor = listing.find('.//div[@class="talalatisor-adatok"]')
            info = adatsor.find('.//div[@class="talalatisor-info adatok"]')

            title = kepsor.find(".//a").get("title")
            url = kepsor.find(".//a").get("href")

            try:
                img = kepsor.find('.//img[@class="img-responsive lazy"]').get(
                    "data-lazyurl"
                )
            except AttributeError:
                img = "NotFound"

            img = loadToCache(img)
            price = adatsor.find('.//div[@class="vetelar"]').text
            listing_id = listing.find(".//*[@data-hirkod]").get("data-hirkod")
            databoxes = info.findall(".//span")
            maybeData = list(map(lambda databox: databox.text, databoxes))

            if None in maybeData:
                # km in tooltip?
                km = info.find('.//abbr[@title="Kilométeróra állása"]')
                if km is not None:
                    finalData = [x if x is not None else km.text for x in maybeData]
                else:
                    finalData = [x if x is not None else "? km" for x in maybeData]

            else:
                finalData = maybeData

            thiscar = car(listing_id, title, url, price, img, " ".join(finalData))
            results.append(thiscar)

    return results
