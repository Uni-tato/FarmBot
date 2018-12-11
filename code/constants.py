from util import FarmbotCSVDialect
import csv

from items import Item
from farm import Crop

CROPS = []
with open("txt/crops.txt", "r") as crops_file:
    reader = csv.DictReader((row for row in crops_file if not row.startswith("#")), dialect=FarmbotCSVDialect)
    for row in reader:
        name = row["name"]         
        time = int(row["time"])
        seed = row["seed"]
        item = row["item"]
        minItem = int(row["minItem"])
        maxItem = int(row["maxItem"])

        CROPS.append(Crop(name, time, seed, item, minItem, maxItem))


ITEMS = []
with open("txt/items.txt", "r") as item_file:
    reader = csv.DictReader((row for row in item_file if not row.startswith("#")), dialect=FarmbotCSVDialect)
    for row in reader:
        name = row["name"]
        buy = row["buy"]
        sell = row["sell"]

        ITEMS.append(Item(name, buy, sell))