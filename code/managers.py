"""Handle syncing of info in `Crop` and `Item` with managers."""
import random
import csv
import json
import copy
import time

from util import FarmbotCSVDialect
from farm import Crop
from items import Item

# Pure Stack overflow magic (https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute)
# behaves like a normal dict but instead of my_dict["foo"] I can do my_dict.foo too
class eventDict(dict):
	def __init__(self, *args, **kwargs):
		super(eventDict, self).__init__(*args, **kwargs)
		self.__dict__ = self

	def __hash__(self):
		return hash(self.name)

	def __eq__(self, other):
		return self.name == other.name

class EventManager:
	"""Manages events"""
	def __init__(self, events_file):
		self.interval = 60
		self.events = []
		# self.active_events[event] returns the events start time
		self.active_events = {}
		#for event in json.loads(events_file)["events"]:
			#self.events.append(eventDict(event))
		self.disabled_plots = {}

		def gen_events_from_list(list_of_events):
			return_list = []
			for thing in list_of_events:
				if isinstance(thing, list):
					return_list.append(gen_events_from_list(thing))
				elif isinstance(thing, dict):
					return_list.append(eventDict(thing))
			return return_list

		self.events = gen_events_from_list(json.loads(events_file)["events"])

	def tick(self, players):
		"""This is where the Event Manager does a tick, and checks to see if any new event has occoured"""

		# Check if any events have finished
		new_active_events = {}
		for event in self.active_events:
			if self.active_events[event] + 86_400 < time.time() - 1000:
			#if self.active_events[event] < time.time() + 100:
				#print(f"ending {event.name}")

				v = random.random()
				try:
					event.triggers
				except Exception:
					continue

				for trigger in event.triggers:
					v -= trigger["probability"]
					if v < 0:
						triggered_event = self.get_event(trigger["name"])
						new_active_events[triggered_event] = time.time()
						break

			else:
				new_active_events[event] = self.active_events[event]
		self.active_events = new_active_events

		def start_event(event):
			#print(f"started {event.name}")
			self.active_events[event] = time.time()
			if "plot_disable" in [effect['type'] for effect in event.effects]:
				probability = [x for x in event.effects if x['type'] == 'plot_disable'][0]['probability']
				for player in players:
					for plot in players[player].farm.plots:
						if random.random() < probability and plot.n != 1:
							plot.disable()

		def parse_list_of_events(list_of_events):
			v = random.random()
			for thing in list_of_events:
				if isinstance(thing, list):
					parse_list_of_events(thing)
				elif isinstance(thing, dict):
					v -= thing.probability
					if v < 0:
						start_event(thing)
						break

		for event in self.events:
			if isinstance(event, list):
				parse_list_of_events(event)
			elif isinstance(event, dict):
				if random.random() < event.probability:
					start_event(event)

	def str(self, i, effect):
		multiplier = self.get(i, effect)

		if multiplier == 1:
			return ""
		else:
			return f" (**x{multiplier}** from events)"

	def get_event(self, name):
		def parse_list(thing):
			if isinstance(thing, list):
				for other_thing in thing:
					result = parse_list(other_thing)
					if result is not None:
						return result
			elif isinstance(thing, dict):
				if thing.name == name:
					return thing
			return None
		return parse_list(self.events)


	def get(self, i, effect):
		for event in self.active_events:
			for event_effect in event.effects:
				if effect == "buy":
					if event_effect["type"] == "buy_change":
						if i in event_effect["affected"] or "*" in event_effect["affected"]:
							return event_effect["multiplier"]

				elif effect == "sell":
					if event_effect["type"] == "sell_change":
						if i in event_effect["affected"] or "*" in event_effect["affected"]:
							return event_effect["multiplier"]

				elif effect == "time":
					if event_effect["type"] == "time_change":
						if i in event_effect["affected"] or "*" in event_effect["affected"]:
							return event_effect["multiplier"]

				elif effect in ("min_item", "max_item"):
					if event_effect["type"] == "item_return_change":
						if i in event_effect["affected"] or "*" in event_effect["affected"]:
							return event_effect["multiplier"]
		return 1

class CropManager:
	"""Manages information about `Crop`s solely by itself.

	This means that there is *one* place that needs to change if crop
	yields, lifetimes, etc. change due to events, for example."""

	def __init__(self, crops_file_text, event_manager):
		self.event_manager = event_manager
		self.crops = []
		# The internal data storage for crops
		self._crops = {}
		# TODO: Implement a general version of the csv parsing.
		reader = csv.DictReader(
			(row for row in crops_file_text if not row.startswith("#")),
			dialect=FarmbotCSVDialect,
		)
		for row in reader:
			min_lifetime = int(row["min_lifetime"])
			max_lifetime = int(row["max_lifetime"])
			self._crops[row["name"]] = {
				"seed": row["seed"],
				"item": row["item"],
				"min_item": int(row["min_item"]),
				"max_item": int(row["max_item"]),
				"min_lifetime": min_lifetime,
				"max_lifetime": max_lifetime,
				"emoji": row["emoji"],
				"time": self._calculate_harvest_time(
					min_lifetime, max_lifetime, row["type"]
				),
				"type": row["type"],
				"unlock_at_lvl": int(row["unlock_at_lvl"]),
				"research_cost": int(row["research_cost"])
			}
			self.crops.append(Crop(row["name"], manager=self))

	@staticmethod
	def _calculate_harvest_time(min_lifetime, max_lifetime, crop_type):
		lifetime = random.randint(min_lifetime, max_lifetime)

		if crop_type == "crop":
			return lifetime
		if crop_type == "tree":
			# An arbitrary number of harvests-- a temporary solution.
			return lifetime / 10

		# TODO: Replace with a non-user-facing error?
		raise ValueError("'{crop_type}' is not a valid crop type.")

	def _get_inner(self, crop, field):
		try:
			crop_info = self._crops[crop]
		except KeyError:
			# TODO: Replace with a non-user-facing error?
			raise ValueError(f"`{crop}` is not a valid crop.")

		return crop_info[field]

	def exists(self, crop):
		"""Check if `crop` is a crop registered with the manager."""
		return crop in self._crops

	def get_time(self, crop):
		"""Get the time that `crop` takes until it is ready to harvest."""
		return self._get_inner(crop, "time") * self.event_manager.get(crop, "time")

	def get_item(self, crop):
		"""Get the name of the `Item` that `crop` yields upon harvest."""
		return self._get_inner(crop, "item")

	def get_seed(self, crop):
		"""Get the seed name of `crop`."""
		return self._get_inner(crop, "seed")

	def get_min_items(self, crop):
		"""Get the minimum number of items `crop` can yield."""
		return self._get_inner(crop, "min_item") * self.event_manager.get(crop, "min_item")

	def get_max_items(self, crop):
		"""Get the maximum number of items `crop` can yield."""
		return self._get_inner(crop, "max_item") * self.event_manager.get(crop, "max_item")

	def get_min_lifetime(self, crop):
		"""Get the minimum time until `crop` can die."""
		return self._get_inner(crop, "min_lifetime")

	def get_max_lifetime(self, crop):
		"""Get the maximum time until `crop` can die."""
		return self._get_inner(crop, "max_lifetime")

	def get_emoji(self, crop):
		"""Get the emoji of `crop`."""
		return self._get_inner(crop, "emoji")

	def get_type(self, crop):
		"""Return whether `crop` is a normal crop ("crop") or "tree"."""
		return self._get_inner(crop, "type")

	def get_unlock_at_lvl(self, crop):
		"""gets the level at which a crop is unlocked."""
		return self._get_inner(crop, "unlock_at_lvl")

	def get_research_cost(self, crop):
		"""gets the amount of research tokens needed to research a crop."""
		return self._get_inner(crop, "research_cost")


class MarketManager:
	"""Manages information (e.g. prices) about `Item`s solely by itself.

	This means that there is *one* place that needs to change if
	prices change due to events, for example."""

	def __init__(self, items_file_text, event_manager):
		self.event_manager = event_manager
		self.items = []
		# The internal data storage for crops
		self._items = {}
		# TODO: Implement a general version of the csv parsing.
		reader = csv.DictReader(
			(row for row in items_file_text if not row.startswith("#")),
			dialect=FarmbotCSVDialect,
		)
		for row in reader:
			self._items[row["name"]] = {
				"buy": float(row["buy"]),
				"sell": float(row["sell"]),
				"emoji": row["emoji"],
				"category": row["category"],
			}
			self.items.append(Item(row["name"], manager=self))

	def _get_inner(self, item, field):
		try:
			item_info = self._items[item]
		except KeyError:
			# TODO: Replace with a non-user-facing error?
			raise ValueError(f"`{item}` is not a valid item.")

		return item_info[field]

	def exists(self, item_name):
		"""Check if `item_name` is an item registered with the manager."""
		return item_name in self._items

	def get_buy_price(self, item_name):
		"""Get price to buy `item_name`."""
		return self._get_inner(item_name, "buy") * self.event_manager.get(item_name, "buy")

	def get_sell_price(self, item_name):
		"""Get price when selling `item_name`."""
		return self._get_inner(item_name, "sell") * self.event_manager.get(item_name, "sell")

	def get_emoji(self, item_name):
		"""Get the emoji of `item_name`."""
		return self._get_inner(item_name, "emoji")

	def get_category(self, item_name):
		"""Get the category of `item_name`."""
		return self._get_inner(item_name, "category")