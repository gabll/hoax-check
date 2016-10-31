from bs4 import BeautifulSoup
from urllib import urlopen
import retinasdk
import credentials
liteClient = retinasdk.LiteClient(credentials.API_KEY)

def url_to_text(url, min_row_length=None):
    """obtain the plain text of the webpage from a url"""
    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    # remove javascript and stylesheet
    for script in soup(["script", "style"]):
        script.extract()
    raw = soup.get_text()
    # break text into lines
    lines = [line.strip() for line in raw.splitlines()]
    # break multi-headlines into a line each
    chunks = [phrase.strip() for line in lines for phrase in line.split("  ")]
    # drop lines under n words
    chunks = [chunk for chunk in chunks if len(chunk.split()) > min_row_length]
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def text_to_keywords(text, n=None):
    """get the first n keywords from a text"""
    return liteClient.getKeywords((u'' + text).encode('utf-8').strip())[:n]

if __name__ == '__main__':
    test_text = url_to_text('http://news.bbc.co.uk/2/hi/health/2284783.stm', 7)
    print text_to_keywords(test_text)
