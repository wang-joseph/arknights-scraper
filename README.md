# arknights-scraper

A small scraper that uses gamepress.gg's easy URLs to find information about Arknights. For when you're too lazy to spin up your browser to find info on the newest operator.

Designed to be a pretty small, simple, and non-instrusive project. This program won't save any information. There may be some formatting errors!

Thanks, [gamepress.gg](https://gamepress.gg/)! :)

## Libraries used

- [requests](https://requests.readthedocs.io/en/master/) (to GET the data)
- [bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) (to help parse through the data)
- [argparse](https://docs.python.org/3/library/argparse.html) (standard lib — so that command line works and is nice to work with)
- [re](https://docs.python.org/3/library/re.html) (standard lib regex — useful for working with strings)
- [json](https://docs.python.org/3/library/json.html) (standard lib — needed for working with JSON)
- [halo](http://halo.josealerma.com/index.html) (literally the best and most important library)

See requirements.txt for the versions of each library.

## To-Do

- [ ] Add operator information
  - [x] ~~Add basic information~~
  - [x] ~~Add support for talents~~
  - [x] ~~Add support for skills~~
  - [x] ~~Add support for stats~~
  - [x] ~~Add support for base skills~~
  - [ ] Add support for upgrade information
- [ ] Add different skill levels, not just max?
- [ ] Add operator comparison?
- [ ] Add stage functionality?
- [ ] Add item descriptions?
- [ ] Add idk other functionality when needed

## Bugs

- Searching "Ethan" - result will be missing a space in the description
