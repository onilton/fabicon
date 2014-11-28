#Fabulous Fabicon Crawler

Fabicon (The Fabulous Favicon Crawler) helps you get better quality favicons, as large as we can find. Perfect for description of websites, but you could find other cool uses. 
Forget about those small ugly .ico files.

## Dependencies

* [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/) -- `sudo apt-get install python-beautifulsoup`
* [tweepy](https://github.com/tweepy/tweepy) -- `sudo pip install tweepy`
* [nose](https://nose.readthedocs.org/en/latest/), [rednose](https://github.com/gfxmonk/rednose) (for testing) -- `sudo pip install nose rednose`

## Usage

### Basic usage 

    ./bin/fabicon --avatar http://thenewyorktimes.com

    ./bin/fabicon -h

	usage: bin/fabicon [-h]
	                  [--avatar | --facebook-pages | --feeds | --feed-language]
	                  [--debug]
	                  TARGET_URL
	
	Get site avatar and some other data from sites.
	
	positional arguments:
	  TARGET_URL            The url or domain that you want to get information
	                        from
	
	optional arguments:
	  -h, --help            show this help message and exit
	  --avatar, --images, -imgs
	                        shows the list of images/avatar for this url or domain
	  --facebook-pages, -fb
	                        shows the list of facebook pages/profiles associated
	                        with this url or domain
	  --feeds               shows the list of feeds that can be found in the url
	                        or domain
	  --feed-language       shows the language for the feed URL provided
	  --debug, -d           enable debugging mode

### Inside code 
	
	import fabicon


## Tests
Just run

	nosetests


	
    
