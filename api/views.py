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
from goose3 import Goose
from rest_framework import status
import codecs
import chardet
from gensim.utils import simple_preprocess
from lexrank import STOPWORDS, LexRank
from nltk.tokenize import sent_tokenize


@api_view(['GET'])
def index(request):
    return Response("The backend-component is running!")


@api_view(['POST'])
def lexrank(request):
    if request.method=='POST':

        print("ok")
        stw = request.POST['stopwords']
        mystopwords = [x.strip() for x in stw.split(',')]
        file = request.FILES['file']
        threshold = request.POST['threshold']
        sentencenumber = request.POST['sentencenumber']
        encoding1 = chardet.detect(file.read())['encoding']
        file.open()  # seek to 0
        utf8_file = codecs.EncodedFile(file, encoding1)
        text = utf8_file.read()
        text = text.decode(encoding1)
        # _doc = Document(text)
        # sentences = _doc.to_sentences()
        text = text.replace('\n', ' ')
        text = text.replace('i.e.', ' i.e')
        text = text.replace('al.', 'al,')
        sentences = lexrank_sum(text, mystopwords, int(sentencenumber), float(threshold))
        print(text)
        return Response({"Text": text, "Sentences": sentences}, status=status.HTTP_200_OK)
    else:
        print('GET NOT ALLOWd')
        return Response({"TEXT":"NOT ALLOWED"}, status=status.HTTP_404_NOT_FOUND)


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
            text = get_text_2(response.text)
            links = get_links(response.text, url)

            r = {'status': 200,
                 'text': text,
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
            abslink = abslink.split('#')[0]
            
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





@api_view(['GET'])
def google_search(request, concept):
    print(concept)
    result = search(concept, stop=20)
    links = []
    for url in result:
        print(url)
        links.append(url)
    r = {'status': 200,
         'text': '',
          'url': url,
          'links': links}

    s = PageSerializer(r)
    return Response(s.data)

    # try:
    #     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    #                              'Chrome/66.0.3359.139 Safari/537.36'}
    #     response = requests.get(url, headers=headers)
    #     # response = requests.get(url)
    #     if response.ok:
    #         r = {'status': 200,
    #              'text': '',
    #              'url': url,
    #              'links': []}

    #     else:
    #         r = {'status': response.status_code,
    #              'text': '',
    #              'url': url,
    #              'links': []}
    #     # print(r)
    #     s = PageSerializer(r)
    # except:
    #     r = {'status': 500,
    #          'text': '',
    #          'url': url,
    #          'links': []}
    #     s = PageSerializer(r)
    # return Response(s.data)



@api_view(['GET'])
def goose_get_text(request, url):
    try:
        sleep(randint(1, 3))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/66.0.3359.139 Safari/537.36'}
        response = requests.get(url, headers=headers)
        g=Goose()
        article = g.extract(raw_html=response.text)
        if response.ok:
            text = article.cleaned_text
            links = get_links(response.text, url)

            r = {'status': 200,
                 'text': text,
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



def lexrank_sum(text, stop_words,

                sentencenumber, threshold):
    doc = list()
    doc.append(text)
    lxr = LexRank(doc, stop_words)
    sentences = list(sent_tokenize(text))
    # get summary with classical LexRank algorithm
    print(sentencenumber)
    summary = lxr.get_summary(sentences, summary_size=sentencenumber, threshold=threshold)
    return summary
#