# Design Document for the Discord bot `Farmbot`

## Summary

This is an idle game where players aim to gain increasingly more money from selling their crop / tree produce.

It can be summarised as follows:

* Players have a farm.
* Farms have plots on them that grow crops and trees.
* After a period of time crops and trees can be harvested for items which can then be sold for money.
* This money can then be used to buy seeds to grow more crops and trees.
* Events (which are global) can impact the price of seeds, crops, etc. for *all* players.

And the cycle continues.


## Message format

### Colour Scheme
* Active messages (things that require attention): 0x00FF00
* Denied (qusetions timed-out or answered False): 0xDDBB8B
* Confirmed (questions answered True): 0xF4D85A
* Info messages (status, inv, tech etc): 0x008C3A

### General:
* All messages should be formal.
* Players should be addresed by a mention (one per message, otherwise use their name).
Names being presented should be marked down (within \`\`).
* Whenever an item name is used it should be proceeded by it's emoji (except in titles).
Ditto for crops/trees.
* Variables (excluding names) (and units) in messages (not within embeds) should be bold.
* Arguments being relayed back treated the same as names.

### Embeds:
* Embed messages should be '\`mention\` ->'.
* Titles should be bold, underlined and start with a capital (no fullstop).
* Field names should be bold, start with a capital and end in ':'.
* Inactive embeds should be entirely struck through.
* Wnen an embed becomes inactive all reactions are to be removed.
* Inactive questions should have a message showing the response.

Unless stated otherwise,
Rules do not apply to debug commands.
All rules *may* be broken *only* under special conditions.
If unsure of how to format something, then dont.


## Code Structure

### EventManager

* Keep track of active events
* Determine what and when events should occur.

### MarketManager

* Manage and store prices (as well as other attributes) for items (e.g. seeds, crop produce).
* Be the sole source for prices so that any event has its effects handled properly.
* Handle any trade between players (if this will be implemented).

### CropManager

* Manage and store information (`minItem`, `maxItem`, min/max lifetime?, etc.) about `Crop`s.
* Be the sole source for crop lifetimes so that any event has its effects handled properly.
* Store the items that can be made from `Crop`s.

### Farm

* Store `Plot`s.
* Has a `name` attribute.

### Plot

* Store `Crop`s.
* Store time left until harvest.
* Handle harvesting and planting logic (with influence from `CropManager`).

### Crop

* Store information about a planted seed (should they just be a plain ID? The `Plot` will manage start and end times).
* Has a minimum and maximum lifetime, within which, the crop *may* be harvested (RNG).

### Tree

* Subclass of `Crop`.
* Has a minimum and maximum lifetime, within which, the tree *may* die (RNG).
* Bears fruit at intervals derived from the lifetime.
* Has a growth, decay period derived from the lifetime.
