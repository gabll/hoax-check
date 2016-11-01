# hoax-check
Automated url fact-checking.

Extracts keywords from a generic url, search combinations of them on [snopes.com](http://www.snopes.com/) and returns the best match.

An API key for the [retinasdk](http://www.cortical.io/resources_apikey.html) is required.
## Usage

    $ python hoax-check.py -h

	usage: hoax-check.py [-h] [--w words_cutoff] [--k keywords_cutoff] [--o no_single_keyword] url

	positional arguments:
	   url                   document url to check for on snopes.com

	optional arguments:
	   -h, --help            show this help message and exit
       --w words_cutoff      cuts off lines with less of n words for keyword extraction (default=7)
       --k keywords_cutoff   consider only the first n relevant keywords (default=4)
       --o no_single_keyword don't search single keywords (default=True)
