# arknights-scraper

A web scraper that uses gamepress.gg's easy URLs to find information about Arknights. For when you're too lazy to spin up your browser to find info on the newest operator.

Designed to be a pretty small and simple project. There may be some formatting errors, so please bear with me!

Thanks, gamepress.gg! :)

Right now the scrapper can only scrape for operators.

## Libraries used

- requests
- bs4
- argparse (so that command line works)

See requirements.txt for the versions

## To-Do

- Add operator information
  - ~~Add basic information~~
  - ~~Add support for talents~~
  - Add support for skills
  - Add support for stats
  - ~~Add support for base skills~~
  - Add support for upgrade information
- Add stage functionality?
- Add item descriptions?
- Add idk other functionality when needed

## Bugs

- Searching "Ethan" - result will be missing a space in the description
