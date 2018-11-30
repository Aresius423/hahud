# Hahud

Használtautó delta - scrape used car listings, and create purty delta views from it.

Running it periodically will show you the new listings, which ones were deleted, and which ones have changed.

## Usage

* Set up your search on hasznaltauto.hu and copy the generated URL
* Add as many queries to queries.py as you wish
* run hahud.py
* run it again some time later to generate a delta view
* open index.html in your browser of choice

### Prerequisites

Tested on python 3.7.1

The following python modules must be installed:

* requests
* lxml

## Generated files

The cache folder contains the thumbnails. This is not maintained, so cleaning it up is your job.

The data_* folders contain the generated sub-pages for the queries, as well as the databases in which the previous snapshot is stored. If you no longer wish to follow a query, remove it from queries.py. If you don't want to see it on the generated page, delete its folder too. To start with a clean sheet, delete the folder and run the script again.

## Licence

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Interactive menu by [Dynamic Drive](http://www.dynamicdrive.com/dynamicindex1/navigate1.htm)
* Idea and some xpath stuff by [@dukkona](https://github.com/dukkona/hasznaltauto)
