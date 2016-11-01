import argparse
import urllib2
from bs4 import BeautifulSoup
import itertools
import retinasdk
import credentials
liteClient = retinasdk.LiteClient(credentials.API_KEY)

def init():
    parser = argparse.ArgumentParser()
    parser.add_argument('document_url', metavar='url', type=str,
                        help='Document url to check for on snopes.com')
    parser.add_argument('--w', metavar='words_cutoff', type=int,
                        default=7,
                        help='Cuts off lines with less of n words for keywords extraction (default=7)')
    parser.add_argument('--k', metavar='keywords_cutoff', type=int,
                        default=4,
                        help='Consider only the first n relevant keywords (default=4)')
    parser.add_argument('--o', metavar='no_single_keyword', type=bool,
                        default=True,
                        help="Don't search single keywords (default=True)")
    global args
    args = vars(parser.parse_args())

def get_soup(url):
    """Create a soup from url"""
    opener = urllib2.build_opener()
    opener.addheader = [('User-agent', "Mozilla/5.0")]
    page = opener.open(url)
    soup = BeautifulSoup(page)
    return soup

def url_to_text(url, min_words=None):
    """obtain the plain text of the webpage from a url"""
    soup = get_soup(url)
    # remove javascript and stylesheet
    for script in soup(["script", "style"]):
        script.extract()
    raw = soup.get_text()
    # break text into lines
    lines = [line.strip() for line in raw.splitlines()]
    # break multi-headlines into a line each
    chunks = [phrase.strip() for line in lines for phrase in line.split("  ")]
    # drop lines under n words
    chunks = [chunk for chunk in chunks if len(chunk.split()) > min_words]
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def text_to_keywords(text, n=None):
    """get the first n keywords from a text"""
    return liteClient.getKeywords((u'' + text).encode('utf-8').strip())[:n]

def get_truth(snopes_href):
    """returns if the rumor is considered true or false"""
    snopes_url = 'http://www.snopes.com' + snopes_href
    soup = get_soup(snopes_url)
    review = soup.find('span', {'itemprop': 'reviewRating'})
    if review:
        if 'rue' in review.string:
            return True
    else:
        review = soup.find('font', {'class': 'status_color'})
        if review:
            if 'TRUE' in review.string:
                return True
    return False

def get_keyword_search(keywords):
    """given a list of keywords, returns the best result (max keywords occurrencies)
     in the snopes.com search serp (first page) if the rumor is not true"""
    search_url = 'http://www.snopes.com/search/?q=%s' % '+'.join(keywords)
    soup = get_soup(search_url)
    serp = soup.find('div', 'search-results')
    if serp: # if exists search-results
        match_list = [len(serp_item.findAll('span', 'highlight'))
                        for serp_item in serp.findAll('div', 'item')
                        if not get_truth(serp_item.find('div', 'text').h3.a['href'])]
        if match_list: # at least one not true
            max_pos = match_list.index(max(match_list))
            article = serp.findAll('div', 'item')[max_pos].find('h3', {'class': 'title'}).a
            return {'title': article.get_text(),
                    'link' : 'http://www.snopes.com' + article['href'],
                    'score': max(match_list)}
    return {'score': 0}

def get_best_result(keyword_set, avoid_ones=True):
    """returns the snopes.com article with the highest keyword match,
    by looking for all the keywords combinations.
    avoid_ones doesn' consider single keyword combinations"""
    search_list = []
    if avoid_ones:
        for i in range(1, len(keyword_set)):
            search_list.extend(list(itertools.combinations(keyword_set, i+1)))
    else:
        for i in range(len(keyword_set)):
            search_list.extend(list(itertools.combinations(keyword_set, i+1)))
    match_list = [get_keyword_search(i) for i in search_list]
    score_list = [i['score'] for i in match_list]
    max_pos = score_list.index(max(score_list))
    if match_list[max_pos] == {'score': 0}:
        return 'No matches on snopes.com for the keyword set extracted from the document.'
    return {'result': match_list[max_pos], 'keywords': search_list[max_pos]}


if __name__ == '__main__':
    # some tests
    # test_text = url_to_text('http://news.bbc.co.uk/2/hi/health/2284783.stm', 7)
    # print text_to_keywords(test_text)
    # print get_truth('/jimmy-john-liautaud-hunting-photos/')
    # print get_truth('/science/stats/blondes.asp')
    # print get_keyword_search(['blonde', 'gene'])
    # print get_keyword_search(['testwithanonsenseword'])
    # print get_best_result(['blonde', 'gene'])
    init()
    document_text = url_to_text(args['document_url'], args['w'])
    document_keywords = text_to_keywords(document_text, args['k'])
    check_result = get_best_result(document_keywords, args['o'])
    print 'Keywords extracted: ', document_keywords
    print 'Best match on snopes.com for the keyword set extracted from the document:'
    print 'Keywords set: ', check_result['keywords']
    print 'Snopes.com title: ', check_result['result']['title']
    print 'Snopes.com link: ', check_result['result']['link']
    print 'Score: ', check_result['result']['score']
