# Create your views here.
from random import randint
from time import sleep
from urllib.parse import urljoin, urlparse  # Python3
import html2text
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from readability import Document
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PageSerializer


@api_view(['GET'])
def check_url(request, url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/66.0.3359.139 Safari/537.36'}
        response = requests.get(url, headers=headers)
        # response = requests.get(url)
        if response.ok:
            r = {'status': 200,
                 'text': '',
                 'url': url,
                 'links': []}

        else:
            r = {'status': response.status_code,
                 'text': '',
                 'url': url,
                 'links': []}
        # print(r)
        s = PageSerializer(r)
        return Response(s.data)

    except:
        r = {'status': 500,
             'text': '',
             'url': url,
             'links': []}
        s = PageSerializer(r)
        return Response(s.data)


@api_view(['GET'])
def check_url_get_text(request, url):
    try:
        sleep(randint(1, 3))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/66.0.3359.139 Safari/537.36'}
        response = requests.get(url, headers=headers)
        # response = requests.get(url)
        if response.ok:
            text = get_text(response.text)
            r = {'status': 200,
                 'text': text,
                 'url': url,
                 'links': []}

        else:
            r = {'status': response.status_code,
                 'text': '',
                 'url': url,
                 'links': []}
        # print(r)
        s = PageSerializer(r)
        return Response(s.data)

    except:
        r = {'status': 500,
             'text': '',
             'url': url,
             'links': []}
        s = PageSerializer(r)
        return Response(s.data)


@api_view(['GET'])
def check_url_get_links(request, url):
    print("Get Links")
    try:
        sleep(randint(1, 3))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/66.0.3359.139 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if response.ok:
            links = get_links(response.text, url)
            r = {'status': 200,
                 'text': '',
                 'url': url,
                 'links': links}

        else:
            r = {'status': response.status_code,
                 'text': '',
                 'url': url,
                 'links': []}
        # print(r)
        s = PageSerializer(r)
        return Response(s.data)

    except:
        r = {'status': 500,
             'text': '',
             'url': url,
             'links': []}
        s = PageSerializer(r)
        return Response(s.data)


def get_links(response, url):
    links = []
    parsed_uri = urlparse(url)
    main_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    soup = BeautifulSoup(response, "html.parser")

    # for link in BeautifulSoup(response, parse_only=SoupStrainer('a')):
    for link in soup.findAll('a'):
        if link.has_attr('href'):
            print(link)
            abslink = urljoin(url, link['href'])
            parsed_uri = urlparse(abslink)
            url_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            if url_domain == main_domain:
                if abslink not in links:
                    if not (abslink.split(".").pop().upper() in ["PDF", "JPG", "PNG", "EXE"]):
                        links.append(abslink)
                    else:
                        print(abslink)

    print(links)
    return links


# def getText(url):
#     try:
#         r = requests.get(url)
#         if r.ok:
#             text = text_from_html(r.text)
#             return {'status' :200,
#                     'text' : text,
#                     'url':url}
#         else:
#             return {'status' :r.status_code,
#                 'text' : '',
#                 'url':url}

#     except:
#          return {'status' :500,
#                 'text' : '',
#                 'url':url}

def get_text(response):
    text = text_from_html(response)
    return text


def get_text_2(response):
    try:
        doc = Document(response)
        text = html2text.html2text(doc.summary())
        return text
    except ValueError:
        print(ValueError)


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]', 'header', 'footer']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)
