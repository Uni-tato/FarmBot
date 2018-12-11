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
