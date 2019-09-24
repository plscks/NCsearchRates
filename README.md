# Nexus Clash Item Search Rates Lookup v1.0

I wrote a couple of scripts one in python 3.7 and the other in node.js, with the end goal of pulling search rates information for [Nexus Clash](https://www.nexusclash.com) directly off of their [wiki page](https://https://wiki.nexuscla.sh/wiki/). It seems like it works rather well.

## searchRates.py
Written in python 3.7 and requiring the [requests module](https://2.python-requests.org/en/master/). This program will hook into the built in API on the Nexus Clash wiki, pull all page ID's from [Category:Current Locations](https://wiki.nexuscla.sh/wiki/index.php?title=Category:Current_Locations). Then it will scan through all of those pages and pull out the relevant item search weights and location base search rates. From there it figures a percent search rate that takes base location search rate into account and no other bonuses or penalties.
If the location page has no [Template:LocationRates](https://wiki.nexuscla.sh/wiki/index.php?title=Template:LocationRates), or an incomplete one, then there is console output reflecting that. If the page has no items listed then there is console output reflecting that.

Usage:

`python -m venv ~/.searchRates`

`. ~/.searchRates/bin/activate`

`python searchRates.py`

## searchRates.js
This one is written with node.js v10.15.2, it was originally a test and prototype to the code that I put into my RRFbot Discord bot that I have been writing with node.js. It's pretty darn straight forward, it takes searchRates.json as a require, as that is essentially where it's database is the it searches through. I did it this way so I wouldn't have to muck about with live active web queries, the database is generated with searchRates.py. When you start it up, it first asks you to type the first letter of the items you'd like to see, this is mostly so you can verify spelling for the item you'd like the odds on. Then it will ask you what the item is. It will print out the list of items starting with what you typed, then it will print out the search odds from searchRates.json for the item you queried. Fairly simple I think. To get it going, you're going to need [node.js](https://nodejs.org/en/). Get that installed, jump to the directory of this repository, make sure package-lock.json is in there for an easy install. This one requires [fs](https://nodejs.org/api/fs.html), but that will mostly install itself, anyways, with node.js installed, package-lock.json in the working directory do this:

`npm install`

`node searchRates.js`
