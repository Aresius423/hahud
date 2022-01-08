from dataclasses import dataclass
from typing import Optional

class query:
    def __init__(self, name, url):
        self.name = name
        self.url = url

@dataclass
class car:
    listing_id: str
    title: str
    url: str
    price: str
    img: str
    data: str
    reason: Optional[str] = None
    detailed_reason: Optional[str] = None


    def __post_init__(self):
        self.price = self.price.replace("\xa0", " ")


    def __eq__(self, other):
        if isinstance(other, car):
            return (
                self.listing_id == other.listing_id
                and self.title == other.title
                and self.url == other.url
                and self.price == other.price
                and self.img == other.img
                and self.data == other.data
            )
        return False


    def with_change_reasons(self, reason: str, detailed_reason: Optional[str] = None) -> 'car':
        return car(self.listing_id,
                   self.title,
                   self.url,
                   self.price,
                   self.img,
                   self.data,
                   reason,
                   detailed_reason,
                  )


    def diffFromOld(self, other) -> str:
        difference = "<p>"
        if self.title != other.title:
            difference += "title changed<br>\n"
        if self.price != other.price:
            difference += f"price changed from {other.price} <br>\n"
        if self.img != other.img:
            difference += "image changed<br>\n"
        if self.data != other.data:
            difference += f"data changed from: {other.data} <br>\n"
        difference += "</p>"
        return difference
