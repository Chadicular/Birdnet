import os

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from urllib import request as req
import shutil


def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    print(e)


def get_bird_types():
    # Get index page
    resp = simple_get('https://nationalzoo.si.edu/scbi/migratorybirds/featured_photo/bird.cfm')
    html = BeautifulSoup(resp, 'html.parser')

    # Find bird types
    pix = html.find(id="pix")
    for option in pix.select('option'):
        bird_name = option.get('value')
        if bird_name is not None:
            get_bird_images(bird_name)


def get_bird_images(bird_name):
    resp = simple_get(
        'https://nationalzoo.si.edu/scbi/migratorybirds/featured_photo/bird.cfm?pix={0}'.format(bird_name))
    html = BeautifulSoup(resp, 'html.parser')

    bird_name = bird_name.replace('/', '_')
    bird_name = bird_name.replace('?', '')

    # Make sure an output folder exists
    if not os.path.exists('birds/{0}'.format(bird_name)):
        os.makedirs('birds/{0}'.format(bird_name))

    print('Downloading images for {0}'.format(bird_name))
    for (i, img) in enumerate(filter(lambda x: x['alt'] == '[Photo]', html.select('img'))):
        i += 1
        bird_link = img['src']
        req.urlretrieve(bird_link, 'birds/{0}/{0}-{1}.jpg'.format(bird_name, i))
        print('Downloading {0}'.format(img['src']))


def main():
    if os.path.exists('birds'):
        shutil.rmtree('birds')

    os.makedirs('birds')

    get_bird_types()


if __name__ == '__main__':
    main()
