from flask import Flask, render_template, g
import BeautifulSoup
import re
import urllib2
import random
import memcache

app = Flask(__name__)

@app.before_request
def before_request():
    g.memcache_client = memcache.Client(["127.0.0.1:11211"])


@app.route('/')
def index():
    # Pick a random page number from quickmeme
    page_num = random.randint(1, 86)

    cache_key = 'rcw_' + str(page_num)

    if g.memcache_client.get(cache_key) == None:
        # Get the page from quickmeme
        page_url = 'http://quickmeme.com/Courage-Wolf/random/?num={0}' \
                    .format(page_num)
        page_html = urllib2.urlopen(page_url).read()
        soup = BeautifulSoup.BeautifulSoup(page_html)

        # Find all links to courage wolves in the page
        links = soup.findAll('a', href=re.compile('^http://www.quickmeme.com/meme/'))

        # Pick the second link from that page, as the first is not a courage wolf
        # for some reason.
        first_link = links[1]

        # Get the image url from that link
        image_url = first_link.img['src']

        # Get the url of the non-thumbnail image
        image_url = image_url.replace("t.qkme.me", "i.qkme.me")

        # Store the result in the cache
        g.memcache_client.set(cache_key, image_url)
    else:
        # If the image url is cached, use it
        image_url = g.memcache_client.get(cache_key)

    return render_template('index.html', image_src=image_url)


if __name__ == '__main__':
    app.run()
