Open Data about Indian General Elections 2014
=============================================

There is no single place to look for data about constituencies, polling stations, number of voters etc. for the upcoming general elections in India. This repo is an attmpt to solve that.

I'm looking for information about the following:

* All Parliamentary Constituencies (PC) in each state
* All Assembly Constituencies (AC) in each PC
* All Polling Booths (PB) in each AC

For each of this, I would like to get as much data as possible. But the current list is:

* number of voters
* number of voters gender-wise
* population
* longitude and latitude or a link to map
* links about this place (including wikipedia link if exists)

And for each past elections (esp. the most recent one)
* voter turnout
* party, candidate name, votes polled for each contested candidate (esp. the winner and runner up)

Data Organization
-----------------

The data is stored in JSON files in `data/` directory. 

The filename of the each location is its unique ID.

KA/PC32.json
KA/AC152.json
KA/AC152/PB0187.json

Web App
-------

I'm planning to buld a webapp to present this information so that anyone can use it with a nice JSON API.


