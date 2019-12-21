class query:
    def __init__(self, name, url):
        self.name = name
        self.url = url


class change:
    def __init__(self, car, summary, reason):
        self.car = car
        self.summary = summary
        self.reason = reason

    def __str__(self):
        return f'{self.reason}\n{str(self.car)}'

    def toListItem(self, template):
        filled = template.replace("%LISTING_REASON%", self.summary)
        filled = filled.replace("%LISTING_ID%", self.car.id)
        filled = filled.replace("%LISTING_PRICE%", self.car.price)
        filled = filled.replace("%LISTING_LINK%", self.car.url)
        filled = filled.replace("%LISTING_TITLE%", self.car.title)
        filled = filled.replace("%LISTING_IMAGE%", self.car.img)
        filled = filled.replace("%DETAILED_REASON%", self.reason)
        filled = filled.replace("%LISTING_DATA%", self.car.data)
        return filled


class car:
    def __init__(self, id, title, url, price, img, data):
        self.id = id
        self.title = title
        self.url = url
        self.price = str(price.replace("\xa0", "&nbsp;"))
        self.img = img
        self.data = data

    def __str__(self):
        return '\n'.join([self.id, self.title, self.price, '___________'])

    def __eq__(self, other):
        if isinstance(other, car):
            return (
                self.id == other.id
                and self.title == other.title
                and self.url == other.url
                and self.price == other.price
                and self.img == other.img
                and self.data == other.data
            )
        return False

    def diffFromOld(self, other) -> str:
        difference = ""
        if self.title != other.title:
            difference += "title changed<br>\n"
        if self.price != other.price:
            difference += f"price changed from {other.price} <br>\n"
        if self.img != other.img:
            difference += "image changed<br>\n"
        if self.data != other.data:
            difference += "data changed from: {other.data} <br>\n"
        return difference
