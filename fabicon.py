#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
from urllib import FancyURLopener
import urlparse
from BeautifulSoup import BeautifulSoup
import sys
import re
import difflib
import gzip
import json
from StringIO import StringIO

import copy

import feedparser

import publicsuffix

import argparse


from guess_language import guess_language
from collections import defaultdict


import socket
# socket.setdefaulttimeout(120)
socket.setdefaulttimeout(60)  # 1 minuto

# multiprocess stuff
from multiprocessing import Process, Queue, current_process
import multiprocessing


def getTwitterAvatar(twitterUsername, size):
    timagelink = urllib.urlopen("https://api.twitter.com/1/users/profile_image?screen_name="+twitterUsername+"&size="+size)
    result = {"url": timagelink.geturl(), "kind": "twitter"}
    timagelink.close()

    return result


def getTwitterRealName(twitterUsername):
    twitterRequest = urllib.urlopen("https://api.twitter.com/1/users/show.json?screen_name="+twitterUsername)
    jdata = json.load(twitterRequest)
    result = jdata["name"]
    twitterRequest.close()

    return result


facebookUsernameExcludeList = ['media', 'permalink.php', 'YOUR_USERNAME', 'photo.php', 'groups', 'sharer.php', 'notes', 'badges', 'business']


def facebookUsername(facebookPageUrl):
    fUsername = re.sub(r'.*(https?:)?//(www\.|[^/]+\.)?facebook\.com/(pages/[^/]+/|profile\.php\?id=|people/[^/]+/)?([A-Za-z_0-9-.]+).*', r'\4', facebookPageUrl)
    return fUsername


def removeRepeated(listWithRepeatedItems):
    seen = set()
    new_l = []
    for d in listWithRepeatedItems:
        # t = tuple(sorted(d.items()))
        t = d
        if t not in seen:
            seen.add(t)
            new_l.append(d)
    # print new_l
    return new_l  # list(set(candidateTags))


def cleanJunk(username):
    excludedChars = u'-_ \t'
    translation_map = dict((ord(char), None) for char in excludedChars)
    username = username.translate(translation_map)

    # remove frequent diff keywords like ['jornal','site','revista','portal'] maybe reduce precision by doing that
    excludedWords = ['jornal', 'site', 'revista', 'portal', 'newspaper', 'online', 'magazine']
    for excludedWord in excludedWords:
        username = username.replace(excludedWord, '')

    return username


def isRelativeUrl(url):
    match = re.match("http://", url)
    return match is None


def isUrlFromRoot(relativeUrl):
    match = re.match("/", relativeUrl)
    return match is not None


# maybe use urlparser ? http://docs.python.org/2/library/urlparse.html#urlparse.urljoin
def getAbsoluteUrl(targetUrl, curPageUrl):
    fixedUrl = re.sub(r'^//', 'http://', targetUrl)  # 9gag crazystuff with // that becomes http://
    domainUrl = ""
    if isRelativeUrl(fixedUrl):
        if isUrlFromRoot(fixedUrl):
            domainUrl = getDomain(curPageUrl)
            fixedUrl = domainUrl+fixedUrl
        else:
            prefixUrl = re.sub(r'(https?://[^?]+)\?', r'\1', curPageUrl)
            prefixUrl = re.sub(r'(https?://[^?]+)/[^/]*$', r'\1', prefixUrl)
            fixedUrl = prefixUrl+"/"+fixedUrl

    return fixedUrl


# Return domain without trailing slash /
def getDomain(url):
    domain = re.sub(r'(https?://[^/]+)/?.*$', r'\1', url)
    return domain


def getRootDomain(url):
    baseurl = re.sub(r'https?://(www\.)?([^/]+)/?.*$', r'\2', url)

    psl = publicsuffix.PublicSuffixList()  # http://pypi.python.org/pypi/publicsuffix/
    pubSuffix = psl.get_public_suffix(baseurl)

    baseurl = pubSuffix

    return baseurl


def isSameRootDomain(url1, url2):
    domain1 = getRootDomain(url1)
    domain2 = getRootDomain(url2)
    return domain1 == domain2


def getName(url):
    baseurl = re.sub(r'https?://(www\.)?([^/]+)/?$', r'\2', url)
    baseurl = re.sub(r'https?://(www\.)?([^/]+)/?([^/]*).*', r'\2 \3', baseurl)
    baseurl = re.sub(r'\.com\.br($|\ )', r'\1', baseurl)
    baseurl = re.sub(r'\.[a-z][a-z]($|\ )', r'\1', baseurl)  # generic for domains with two letters Ex: .pt
    baseurl = re.sub(r'\.com($|\ )', r'\1', baseurl)
    baseurl = re.sub(r'\.net($|\ )', r'\1', baseurl)
    baseurl = re.sub(r'\.org($|\ )', r'\1', baseurl)
    baseurl = re.sub(r'\.org\.br($|\ )', r'\1', baseurl)

    return unicode(baseurl.lower())

facebookUrls = []


def getFacebookPages(url, debug=False):
    # global facebookUrls we do not need to change this
    candidateTags = getCandidateTags(url)
    facebookPages = []
    print "FACEBOOK LINKS!!! "

    for facebookUrl in facebookUrls:
        facebookPages.append({'username': facebookUsername(facebookUrl), 'url': facebookUrl})
        print "facebookurl="+facebookUrl.encode('utf-8')
    return facebookPages


# Change urllib user-agent
class BuskOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

# http://stackoverflow.com/questions/2318446/how-to-follow-meta-refreshes-in-python


def getHopsAndSource(url, downloadDebug=False):
    redirect_re = re.compile('<meta[^>]*?url=(.*?)["\']', re.IGNORECASE)
    comments = re.compile(r'<!--.*?-->')

    buskOpener = BuskOpener()

    hops = []
    while url:
        if downloadDebug:
            print hops
        if url in hops:
            url = None
        else:
            hops.insert(0, url)
            # response = urllib.urlopen(url)
            response = buskOpener.open(url)
            if downloadDebug:
                print "Opened url:", url
            if response.geturl() != url:
                hops.insert(0, response.geturl())

            htmlSource = response.read()
            # Treat gzip encoding  http://www.diveintopython.net/http_web_services/gzip_compression.html
                # If data came back gzip-compressed, decompress it
            if response.headers.get('content-encoding', '') == 'gzip':
                htmlSource = gzip.GzipFile(fileobj=StringIO(htmlSource)).read()

            # remove browser comments and hacks as in
            # <!--[if lte IE 6]><meta http-equiv="refresh" content="0; url=/paginas/error-ie6/" /> -->
            htmlSource = comments.sub('', htmlSource)

            # check for redirect meta tag
            match = redirect_re.search(htmlSource)
            if match:
                url = urlparse.urljoin(url, match.groups()[0].strip())
                print "Hop (meta referesh) to", url
            else:
                url = None
    return (hops, response, htmlSource)


def getSoupParser(htmlSource):
    # Tuple to treat really bad html (crazy comments like <!- ->) (regular expression, replacement function)
    # Examples
    #	www.zupi.com.br has <!– fim da id logo –> --> it is not - it is –
    myMassage = [(re.compile(r'<!([^->]+)>'), lambda match: '<!--' + match.group(1) + '-->'),
                 (re.compile(r'<!--([^->]+)>'), lambda match: '<!--' + match.group(1) + '-->'),
                 (re.compile(r'<!([^->]+)-->'), lambda match: '<!--' + match.group(1) + '-->')
                 ]

    # Dealing with crazy html and comments as in
    # http://www.crummy.com/software/BeautifulSoup/bs3/documentation.html#Sanitizing Bad Data with Regexps
    myNewMassage = copy.copy(BeautifulSoup.MARKUP_MASSAGE)
    myNewMassage.extend(myMassage)

    soup = BeautifulSoup(htmlSource, markupMassage=myNewMassage)
    return soup


def downloadFeedAndGetLanguage(feedUrl, debug=False):
    feed = feedparser.parse(feedUrl)
    # print feed
    return getFeedLanguage(feed, debug)


def getFeedLanguage(feed, debug=False):
    print "Feed:", feed.feed.title

    langCount = defaultdict(int)
    guessed_lang = guess_language(feed.feed.title)  # .encode('utf-8')
    langCount[guessed_lang] += 2
    for entry in feed.entries[:10]:

        if hasattr(entry, 'title'):
            txtValue = entry.title
            # print entry.title

            soup = getSoupParser(txtValue)
            txtValue = ' '.join(soup.findAll(text=True))
            if debug:
                print "entry-title:", txtValue
            guessed_lang = guess_language(txtValue)
            langCount[guessed_lang] += 1

        # print entry
        if hasattr(entry, 'summary'):
            txtValue = entry.summary
            soup = getSoupParser(txtValue)
            txtValue = ' '.join(soup.findAll(text=True))
            if debug:
                print "entry-summary:", txtValue
            guessed_lang = guess_language(txtValue)
            langCount[guessed_lang] += 1

        # print entry.content[0]
        if hasattr(entry, 'content'):
            allContents = ' '.join([content.value for content in entry.content])
            print allContents
            soup = getSoupParser(txtValue)
            txtValue = ' '.join(soup.findAll(text=True))
            if debug:
                print "entry-allcontents:", txtValue
            guessed_lang = guess_language(txtValue)
            langCount[guessed_lang] += 1

    langCount['UNKNOWN'] = 0

    if debug:
        print "langCount:", langCount
    key, value = max(langCount.iteritems(), key=lambda x: x[1])
    return key
    # return guess_language(feed.title)


def feedCheckerWorker(work_queue, feedUrlsQueue, commonUrls):
    # try:
    for url in iter(work_queue.get, 'STOP'):
    # print "Checking Url..."
        feedParserSuccess = True
        try:
            feedFile = feedparser.parse(url)
        except Exception as e:
            feedParserSuccess = False

        try:
            # place result on feedUrlsQueue or in not
            if feedParserSuccess and hasattr(feedFile, 'version') and feedFile.version != '':
                # Feeds with entries <=2 probably are not working or are dead feeds
                #if len(feedFile.entries) > 2:
                feedUrlsQueue.put({"url": feedFile.href, "url_original": url, "title": feedFile.feed.get("title", "Sem titulo"), "kind": "href "+feedFile.version, "entries_count": len(feedFile.entries)})
                # print "Feed =",url
            else:
                # print "Not feed =",url
                commonUrls.put(url)
            # commonUrls.put(url)
        except Exception, e:
            commonUrls.put(url)
            print e

    print "Got STOP %s ." % (current_process().name)
        # pass
    # return True


def emptyQueues(feedUrlsQueue, feedUrlsList, commonUrlsQueue, commonUrlsList):  # jobs,queues,gotQueues)
    while not feedUrlsQueue.empty():
        feed = feedUrlsQueue.get()
        # print "Emptying... feed",feed['url']
        feedUrlsList.append(feed)

    while not commonUrlsQueue.empty():
        url = commonUrlsQueue.get()
        # print "Emptying... url",url
        commonUrlsList.append(url)


def checkIfUrlsAreFeeds(urls):
    # numWorkers = multiprocessing.cpu_count()*2 #just one to make less heavy
    numWorkers = multiprocessing.cpu_count()
    if len(urls) > numWorkers:
        workers = numWorkers
    else:
        workers = len(urls)

    print "Using", workers, "workers..."

    # print workers
    work_queue = Queue()
    feedUrlsQueue = Queue()
    commonUrlsQueue = Queue()
    processes = []

    for url in urls:
        work_queue.put(url)

    for w in xrange(workers):
        p = Process(target=feedCheckerWorker, args=(work_queue, feedUrlsQueue, commonUrlsQueue))
        p.start()
        processes.append(p)
        work_queue.put('STOP')

    print "End starting workers"

    feedUrlsList = []
    commonUrlsList = []
    # Need because of "bug" http://bugs.python.org/issue8426 workarounded in http://stackoverflow.com/a/11855207/1706351
    import time
    n = 1
    while any([proc.is_alive() for proc in processes]):
        n += 1
        time.sleep(5)  # Wait a fixed time of 5 seconds to read from the queue
        emptyQueues(feedUrlsQueue, feedUrlsList, commonUrlsQueue, commonUrlsList)  # jobs,queues,gotQueues)

    pnumber = 1
    for p in processes:
        p.join()
        print "Joined process", pnumber
        pnumber = pnumber + 1

    print "End joining workers"

    feedUrlsQueue.put('STOP')
    for feed in iter(feedUrlsQueue.get, 'STOP'):
        feedUrlsList.append(feed)

    commonUrlsQueue.put('STOP')
    for url in iter(commonUrlsQueue.get, 'STOP'):
        commonUrlsList.append(url)

    return (feedUrlsList, commonUrlsList)


def getFeeds(url, enableMetaTagSearch=True, visitedUrls=[], checkedFeedUrls=set(), checkedNonFeedUrls=set(), deepLevel=0, debug=False, downloadDebug=False, min_entries=3):
    allFeedUrls, returnedVisitedUrls, returnedCheckedNonFeedUrls = getFeedsAndNonFeeds(url, enableMetaTagSearch=True, visitedUrls=visitedUrls, checkedFeedUrls=checkedFeedUrls, checkedNonFeedUrls=checkedNonFeedUrls, deepLevel=0, debug=debug, downloadDebug=downloadDebug)
    filteredAllFeedUrls = [ feed for feed in allFeedUrls if feed["entries_count"]>=min_entries ] 
    return filteredAllFeedUrls


def getFeedsAndNonFeeds(url, enableMetaTagSearch=True, visitedUrls=[], checkedFeedUrls=set(), checkedNonFeedUrls=set(), deepLevel=0, debug=False, downloadDebug=False):
    feedUrls = []
    # Try to download page, otherwise, fail gracefully

    if debug:
        print """[Level=%d] Getting url %s""" % (deepLevel+1, url)
    try:
        hops, page, htmlSource = getHopsAndSource(url, downloadDebug)
        soup = getSoupParser(htmlSource)
        # print soup
    except Exception as e:
        if debug:
            print "Exception for:", url
        return feedUrls, set([url]), set()

    finalUrl = page.geturl()
    if debug:
        print """[Level=%d] Got url %s  FinalUrl: %s""" % (deepLevel+1, url, finalUrl)

    localVisitedUrls = visitedUrls[:]

    localCheckedFeedUrls = checkedFeedUrls.copy()
    localCheckedNonFeedUrls = checkedNonFeedUrls.copy()

    # If the url was already seen, do nothing, stop and return
    if finalUrl in localVisitedUrls or url in localVisitedUrls:
        return feedUrls, localVisitedUrls, localCheckedNonFeedUrls

    localVisitedUrls.append(url)
    localVisitedUrls.append(finalUrl)

    deepLevel += 1
    if deepLevel > 2:
        if debug:
            print """[Level=%d] Ending crawl for url %s  (FinalUrl: %s)""" % (deepLevel, url, finalUrl)
        return feedUrls, localVisitedUrls, localCheckedNonFeedUrls #localVisitedUrls 

    # Follow (i)frames on first page when htmlSource is too small. Even if it
    # points to another domain, probably it's something like a redirect.
    # The risk of goint to another site/domain not related to original
    # one is low when the html length is small.
    if deepLevel == 1 and len(htmlSource) <= 2000:
        if debug:
            print "Looking for iframes in :", finalUrl

        iframes = soup.findAll(['frame', 'iframe'])

        if debug:
            print "Iframes found in ", finalUrl, ":", len(iframes)
            print "htmlSource size", len(htmlSource)

        for iframe in iframes:
            if 'src' in dict(iframe.attrs):
                iframeSrc = getAbsoluteUrl(iframe['src'], finalUrl)
                if iframeSrc not in localVisitedUrls:
                    if debug:
                        print "Searching for more in iframe url:", iframeSrc
                    otherFeedUrls, returnedVisitedUrls, returnedCheckedNonFeedUrls = getFeedsAndNonFeeds(iframeSrc, enableMetaTagSearch=True, visitedUrls=localVisitedUrls, checkedFeedUrls=localCheckedFeedUrls, checkedNonFeedUrls=localCheckedNonFeedUrls, deepLevel=(deepLevel-1), debug=debug)
                    localVisitedUrls.append(iframeSrc)

                    localCheckedNonFeedUrls = localCheckedNonFeedUrls.copy().union(returnedCheckedNonFeedUrls)

                    feedUrls = feedUrls + otherFeedUrls

    urlsToCheck = set()
    if enableMetaTagSearch:
        feedLinkTags = soup.findAll('link', attrs={"rel": "alternate", "type": re.compile(r'application/(atom|rss)\+xml|text/xml')})
        # if debug: print "Feeds found in",len(feedLinkTags),"by meta:",finalUrl
        for feedLinkTag in feedLinkTags:
            fixedUrl = getAbsoluteUrl(feedLinkTag['href'], finalUrl)
            if debug:
                print "Going to check Mega tag feedUrl:", fixedUrl, feedLinkTag.get("title", "Sem Nome").encode('utf-8'), "link "+feedLinkTag["type"]
            if fixedUrl not in localVisitedUrls and fixedUrl not in localCheckedFeedUrls:
                urlsToCheck.add(fixedUrl)

    feedAnchorTags = soup.findAll('a', attrs={"href": re.compile(r'rss|feed|xml')})
    # Now try to match from anchor content/text <a ref="">RSS</a>
    for anchorText in soup.findAll(lambda tag: tag.name == 'a' and re.findall(r"rss|feed|xml", tag.text, re.IGNORECASE)):
        # print "anchorText=",anchorText
        feedAnchorTags.append(anchorText)

    feedAnchorPossibleFeedUrls = set()
    alreadyCheckedCommonUrls = set()
    
    for feedAnchorTag in feedAnchorTags:
        if 'href' in dict(feedAnchorTag.attrs):
            # print "going to check", feedAnchorTag['href']
            fixedUrl = getAbsoluteUrl(feedAnchorTag['href'], finalUrl)
            fixedUrl = re.sub(r'^.*http://add\.my\.yahoo\.com/rss\?url=(https?)(%3A|:)//',r'\1://', fixedUrl)
            # print "going to check candidate feed", fixedUrl
            if fixedUrl not in localVisitedUrls and fixedUrl not in localCheckedFeedUrls and fixedUrl not in localCheckedNonFeedUrls :
                urlsToCheck.add(fixedUrl)
                feedAnchorPossibleFeedUrls.add(fixedUrl)
            if fixedUrl not in localVisitedUrls and fixedUrl in localCheckedNonFeedUrls :
                alreadyCheckedCommonUrls.add(fixedUrl)

    if debug:
        print """[Level=%d] Possible feed urls from anchors for url %s  FinalUrl: %s""" % (deepLevel, url, finalUrl)
    for possibleFeedUrl in feedAnchorPossibleFeedUrls:
            if debug:
                print ("\t"+possibleFeedUrl) 

    # If we are in the first level of the crawl,
    # Adds common urls that gives rss
    # In some sites you can't find the rss in meta or in links,
    # but the CMS still exposes it through some urls patterns
    # This is our try to catch them....
    frequentFeedUrlsSet = set()
    if deepLevel == 1:
        frequentFeedUrlPatterns = ['feed',
                                   'feeds',
                                   'atom',
                                   'rss',
                                   'feed/rss',
                                   'feed/atom',
                                   '?feed=rss2',  # Default for wordpress
                                   '?feed=rss',   # Info here:
                                   '?feed=atom',  # http://codex.wordpress.org/WordPress_Feeds
                                   'feeds/posts/default',          # Default for blogger
                                   'feeds/posts/default?alt=rss',  # http://support.google.com/blogger/bin/answer.py?hl=pt&answer=97933
                                   'rss.xml',  # Default for Drupal (and some other sites) http://drupal.org/node/111018
                                               # and http://stackoverflow.com/a/1644621/1706351
                                   '?option=com_content&view=featured&format=feed&type=rss',  # for joomla from
                                   '?option=com_content&view=featured&format=feed&type=atom',  # http://stackoverflow.com/a/14806742/1706351
                                   'index.xml',      # 50 (frequency) common patterns from a list of feeds
                                   'rss.php',        # 23
                                   'rss/rss.xml',    # 16
                                   'Rss2.xml',       # 15
                                   'rss/index.xml',  # 14
                                   'feed.rss',       # 14
                                   'index.rss',      # 13
                                   'rss.asp',        # 10
                                   'feed.xml',       # 6
                                   'atom.xml'        # 6
                                   ]

        for frequentFeedUrlPattern in frequentFeedUrlPatterns:
            frequentFeedUrlsSet.add(getAbsoluteUrl(frequentFeedUrlPattern, finalUrl))
            frequentFeedUrlsSet.add(getAbsoluteUrl('/'+frequentFeedUrlPattern, finalUrl))

        if debug:
            print "Frequent feed urls patterns that will be checked"
        for frequentFeedUrl in frequentFeedUrlsSet:
            if debug:
                print ("\t"+frequentFeedUrl) 
            if frequentFeedUrl not in localVisitedUrls and frequentFeedUrl not in localCheckedFeedUrls:
                urlsToCheck.add(frequentFeedUrl)

    print """[Level=%d] Urls que serao verificadas para url %s (%s) : %d""" % (deepLevel, url, finalUrl, len(urlsToCheck))

    checkedFeedUrls, commonUrls = checkIfUrlsAreFeeds(urlsToCheck)

    print """[Level=%d] Feeds encontrados para para url %s (%s) : %d""" % (deepLevel, url, finalUrl, len(checkedFeedUrls))


    feedUrls = feedUrls[:] + checkedFeedUrls[:]

    listOfFeedUrls = [ feed.get("url","") for feed in feedUrls ]
    listOfOriginalFeedUrls = [ feed.get("url_original","") for feed in feedUrls ]
    
    localCheckedFeedUrls = localCheckedFeedUrls.copy().union(set(listOfFeedUrls))
    localCheckedFeedUrls = localCheckedFeedUrls.union(set(listOfOriginalFeedUrls))


    localCheckedNonFeedUrls = localCheckedNonFeedUrls.copy().union(set(commonUrls[:]))

    print """[Level=%d] Urls não conhecidas que não são feeds encontradas para url %s : %d""" % (deepLevel, finalUrl, len(commonUrls))
    #Merge commonUrls with urls already checked previously 
    commonUrls = commonUrls[:] + list(alreadyCheckedCommonUrls)
    print """[Level=%d] Total urls que não são feeds encontradas para url %s : %d""" % (deepLevel, finalUrl, len(commonUrls))

    # for commonUrl in commonUrls:
        # print "Going to crawl url", commonUrl

    for commonUrl in commonUrls:
        if commonUrl not in frequentFeedUrlsSet or commonUrl in feedAnchorPossibleFeedUrls:
            # if has .xml or .rss extesion it's not a url to follow, it just a broken feed, so do nothing
            if (not re.findall(r"(\.xml|\.rss)$", commonUrl, re.IGNORECASE)):  # and not re.findall(r"Comedy", commonUrl, re.IGNORECASE)):
            # if (not re.findall(r"(\.xml|\.rss)$", commonUrl, re.IGNORECASE) and not re.findall(r"Comedy", commonUrl, re.IGNORECASE)):
                if commonUrl not in localVisitedUrls:
                    if (isSameRootDomain(url, commonUrl) or isSameRootDomain(finalUrl, commonUrl)):
                        if deepLevel < 2:
                            if debug:
                                print "Searching for more in url:", commonUrl
                            
                            #No reason to crawl those since they will be already crawled in next loop iteration
                            commonUrlsSetWithoutCurrent = set(commonUrls)
                            commonUrlsSetWithoutCurrent.remove(commonUrl)
                            urlsNotToCrawl = localVisitedUrls[:] + list(commonUrlsSetWithoutCurrent)

                            otherFeedUrls, returnedVisitedUrls, returnedCheckedNonFeedUrls = getFeedsAndNonFeeds(commonUrl, enableMetaTagSearch=False, visitedUrls=urlsNotToCrawl, checkedFeedUrls=localCheckedFeedUrls, checkedNonFeedUrls=localCheckedNonFeedUrls, deepLevel=deepLevel, debug=debug)
                            localVisitedUrls.append(commonUrl)

                            localCheckedNonFeedUrls = localCheckedNonFeedUrls.copy().union(returnedCheckedNonFeedUrls)

                            feedUrls = feedUrls + otherFeedUrls[:]

                            listOfFeedUrls = [ feed.get("url","") for feed in feedUrls ]
                            listOfOriginalFeedUrls = [ feed.get("url_original","") for feed in feedUrls ]
                            
                            localCheckedFeedUrls = localCheckedFeedUrls.copy().union(set(listOfFeedUrls))
                            localCheckedFeedUrls = localCheckedFeedUrls.union(set(listOfOriginalFeedUrls))
                        else:
                            if debug:
                                print "There's no reason to crawl cause we won't do anything with the url:", commonUrl
                    else:
                        if debug:
                            print "Ignoring", commonUrl, "since it is not from same domain as", url
                else:
                    if debug:
                        print "Ignoring", commonUrl, "since it is in localVisitedUrls"
            else:
                if debug:
                    print "Ignoring", commonUrl, "since it's probably a broken feed"
        else:
            if debug:
                print "Ignoring", commonUrl, "since this url was just a bad guess from us based on common feed urls patterns. This link wasn't REALLY in the site."

    listWithRepeatedItems = list(feedUrls)
    seen = set()
    new_l = []
    for d in listWithRepeatedItems:
        t = d['url']
        if t not in seen:
            seen.add(t)
            new_l.append(d)
    feedUrls = list(new_l)

    # remove /algumacoisa/../outracoisa from urls and replace with /outracoisa http://www.intelog.net/site/../ArtigosNoticias/Arquivos/rss_619181.xml
    for newFeed in feedUrls:
        newFeed['url'] = re.sub(r'/[^/]*/\.\./', r'/', newFeed['url'])

    # remove /algumacoisa/./outracoisa from urls and replace with /algumacoisa/outracoisa http://cartamaior.com.br/templates/././feed/pt-br/feed_Destaques.xml
    for newFeed in feedUrls:
        newFeed['url'] = re.sub(r'/\./', r'/', newFeed['url'])

    # feedUrls = removeRepeated(feedUrls)
    print "ENDED getFeedsAndNonFeeds for", url
    return feedUrls, localVisitedUrls, localCheckedNonFeedUrls


def getCandidateTags(url, debug=False, staticHtml=""):
    # reload(sys)
    # sys.setdefaultencoding("utf-8")
    # print "Download url..."
    # page = urllib.urlopen(url))
    # if debug:
    #	print page.headers['content-type']
    #	#print str(page)
    #
    # print "Downloaded!"
    # htmlSource=page.read()
    # Treat gzip encoding  http://www.diveintopython.net/http_web_services/gzip_compression.html
    ## If data came back gzip-compressed, decompress it
    # if page.headers.get('content-encoding', '') == 'gzip':
    #    htmlSource = gzip.GzipFile(fileobj=StringIO(htmlSource)).read()

    if len(staticHtml) == 0:
        hops, page, htmlSource = getHopsAndSource(url)

        finalUrl = page.geturl()
        print "FinalUrl:", finalUrl
    else:
        htmlSource = staticHtml
        finalUrl = url

    print "########END URLLIBREQUEST############"

    # print htmlSource

    soup = getSoupParser(htmlSource)

    candidateTags = []

    print "image_src..."
    # Try to get image_src icons
    imgSrcTags = soup.findAll('link', attrs={"rel": "image_src"})
    for imgSrcTag in imgSrcTags:
        fixedUrl = getAbsoluteUrl(imgSrcTag['href'], finalUrl)
        candidateTags.append({"url": fixedUrl, "kind": "image_src"})

    print "Apple icons..."
    # Try to get apple style icons
    appleTags = soup.findAll('link', attrs={"rel": ["apple-touch-icon-precomposed", "apple-touch-icon"]})
    for appleTag in appleTags:
        fixedUrl = getAbsoluteUrl(appleTag['href'], finalUrl)
        candidateTags.append({"url": fixedUrl, "kind": "apple"})

    print "Open graph icons..."
    # Try to get open graph (facebook) image
    openGraphTags = soup.findAll('meta', attrs={"property": "og:image"})

    for openGraphTag in openGraphTags:
        fixedUrl = getAbsoluteUrl(openGraphTag['content'], finalUrl)
        candidateTags.append({"url": fixedUrl, "kind": "openGraph"})

    print "Facebook page..."
    global facebookUrls

    facebookUrls = []

    # Widget, but is not a page, it's a regular user
    facebookUrlsFromWidget = soup.findAll(['fb:fan'], attrs={"profile_id": True})
    for facebookUrl in facebookUrlsFromWidget:
        likeBoxProfileId = facebookUrl['profile_id']
        if likeBoxProfileId not in facebookUsernameExcludeList:
            facebookUrls.append(likeBoxProfileId)
            print "facebookurlfromwidget:", likeBoxProfileId

    facebookUrlsFromWidget = soup.findAll(['fb:like-box'])  # , attrs={"href" : re.compile(r'https?://(www\.)?twitter\.com/(\#\!/)?[^/]/?')})
    for facebookUrl in facebookUrlsFromWidget:
        likeBoxHref = facebookUrl['href']
        if facebookUsername(likeBoxHref) not in facebookUsernameExcludeList:
            facebookUrls.append(likeBoxHref)
            print "facebookurlfromwidget:", likeBoxHref

    facebookUrlsFromLinks = soup.findAll(['a', 'area', 'fb:like'], attrs={"href": re.compile(r'https?(://|%3A%2F%2F)(www\.|[^/]+\.)?facebook\.com(/|%2F)')})
    for facebookUrl in facebookUrlsFromLinks:
        facebookUrlHref = urllib.unquote(facebookUrl['href'])

        facebookUrlHref = re.sub(r'facebook\.com/home\.php\?#(%21|!)?/pages/', r'facebook.com/pages/', facebookUrlHref)  # fix http://colunas.globorural.globo.com/planetabicho
        facebookUrlHref = re.sub(r'.*(https?://(www\.|[^/]+\.)?facebook\.com/(pages/[^/]+/|profile\.php\?id=|people/[^/]+/)?[A-Za-z_0-9-.]+).*', r'\1', facebookUrlHref)  # fix g1

        if facebookUsername(facebookUrlHref) not in facebookUsernameExcludeList:
            facebookUrls.append(facebookUrlHref)
            print "facebookurlfromlinks:", facebookUrlHref.encode("utf-8")

    # iframes from like buttons (plugins)
    facebookUrlsFromIframes = soup.findAll(['iframe'], attrs={"src": re.compile(r'^.*?/plugins/.*?(https?:)?(:?//|%3A%2F%2F)(www\.|[^/]+\.)?facebook\.com(/|%2F)')})
    facebookUrlsFromIframes += soup.findAll(['iframe'], attrs={"src": re.compile(r'^.*?facebook\.com/plugins/likebox.php\?.*?id=[0-9]+')})
    for facebookIframe in facebookUrlsFromIframes:
        iframeSrc = urllib.unquote(facebookIframe['src'])

        iframeSrc = re.sub(r'^.*?/plugins/.*?((https?:)?//(www\.)?facebook\.com/(pages/[^/]+/)?[A-Za-z_0-9-.]+).*', r'\1', iframeSrc)
        iframeSrc = re.sub(r'^.*?facebook\.com/plugins/likebox.php\?.*?id=([0-9]+).*?$', r'\1', iframeSrc)  # get only the id

        if facebookUsername(iframeSrc) not in facebookUsernameExcludeList:
            facebookUrls.append(iframeSrc)
            print "facebookurlfromiframes:", iframeSrc.encode('utf-8')

    # div like box as in http://www.gamespower.com.br/
    facebookLikeBoxes = soup.findAll(['div'], attrs={"data-href": re.compile(r'(https?:)?//(www\.)?facebook\.com/')})
    for facebookLikeBox in facebookLikeBoxes:
        dataHref = facebookLikeBox['data-href']
        dataHref = re.sub(r'^.*?/plugins/.*?((https?:)??//(www\.)?facebook\.com/(pages/[^/]+/)?[A-Za-z_0-9-.]+).*', r'\1', dataHref)
        if facebookUsername(dataHref) not in facebookUsernameExcludeList:
            facebookUrls.append(dataHref)
            print "facebookurlfromiframes:", dataHref

    facebookUrls = removeRepeated(facebookUrls)

    # TODO USE facebook access token
    # Some not public facebook pages do not work, teste case: http://gamerexperience.blogspot.com/
    # Get an access token here
    # https://developers.facebook.com/tools/explorer/145634995501895/?method=GET&path=695420378%3Ffields%3Did%2Cname
    # fbAccessToken="AAACEdEose0cBAGpExr0GdO5vLFaDlMEuc3bG711EvhB79ttklvDEmAdyeJ1tNKAgt9V53TgQNpUGZAfKiTf2QeDLg1tylZAqHfeLdUMAZDZD"

    for facebookUrl in facebookUrls:
        fbUsername = facebookUsername(facebookUrl)
        candidateTags.append({"url": "https://graph.facebook.com/"+fbUsername+"/picture?type=normal", "kind": "facebook"})
        candidateTags.append({"url": "https://graph.facebook.com/"+fbUsername+"/picture?width=150&height=150", "kind": "facebook"})
        candidateTags.append({"url": "https://graph.facebook.com/"+fbUsername+"/picture?width=500", "kind": "facebook"})
        # candidateTags.append({"url" : "https://graph.facebook.com/"+fbUsername+"/picture?type=normal&access_token="+fbAccessToken, "kind" : "facebook"})
        # candidateTags.append({"url" : "https://graph.facebook.com/"+fbUsername+"/picture?width=500&access_token="+fbAccessToken, "kind" : "facebook"})

    print "Twitter icons..."

    # Get all twitter links
    allLinks = soup.findAll(['a', 'area'], attrs={"href": re.compile(r'https?://(www\.)?twitter\.com/(\#\!/|intent/user\?region=following&screen_name=)?[^/]/?')})

    print "#####END SOUP #####"

    if debug:
        tests = soup.findAll(debug)
    else:
        tests = []
    for test in tests:
        if test is not None:
            if len(test.contents) > 0:
                if len(str(test.contents)) > 1:
                    # print str(test.contents ),str(test.name)
                    print str(test.name), str(test.attrs), str(test.values)

    print "Twitter Links:", len(allLinks)
    for tlink in allLinks:
        # print tlink['href']
        tusername = re.sub(r'https?://(www\.)?twitter\.com/(\#\!/|intent/user\?region=following&screen_name=)?([A-Za-z0-9_-]+)/?.*', r'\3', tlink['href'])
        # https://twitter.com/intent/user?region=following&screen_name=Kotaku&source=followbutton&variant=1.1
        tusername = tusername.lower()
        # print tusername

        # if we don't have a explicit link to twitter profile but have a share we get it also ;) Ex: omelete.uol.com.br
        if tusername == "share":
            if tlink.get('data-via', '') != '':
                tusername = tlink['data-via']

        # TODO in urls permutate and remove to try to get the exact thing: blogs.ne10.uol = ne10.uol and blogs.ne10 or ne10 or uol ne10
        # TODO use twitter profile name to match also instead of just username
        # TODO maybe use twitter profile info link to give some confidence?
        domainName = getName(url)
        cleanDomainName = cleanJunk(domainName)
        cleanTwtUsername = cleanJunk(tusername)
        txtsimil = difflib.SequenceMatcher(None, cleanDomainName, cleanTwtUsername).ratio()
        print "Domainname:", domainName, "("+cleanDomainName+")", "Twitter:", tusername, "("+cleanTwtUsername+")", "Similarity:", txtsimil

        if (txtsimil <= 0.6 and tusername != "share" and tusername != "search" and tusername != "statuses"):
            print "Username didn't work, trying with twitter real (full) name"
            tRealName = getTwitterRealName(tusername)
            cleanTwtRealName = cleanJunk(tRealName)
            txtsimil = difflib.SequenceMatcher(None, cleanDomainName, cleanTwtRealName).ratio()
            print "Domainname:", domainName, "("+cleanDomainName+")", "TwitterRealName:", tRealName.encode("utf-8"), "("+cleanTwtRealName.encode("utf-8")+")", "Similarity:", txtsimil

        if (tusername != "share" and txtsimil > 0.6):
            # timagelink = urllib.urlopen("https://api.twitter.com/1/users/profile_image?screen_name="+tusername+"&size=original")
            # candidateTags.append({"url" : timagelink.geturl(), "kind" : "twitter"})
            # print str(timagelink.geturl())
            # timagelink.close()
            candidateTags.append({"url": "https://api.twitter.com/1/users/profile_image?screen_name="+tusername+"&size=original", "kind": "twitter"})

            # timagelink = urllib.urlopen("https://api.twitter.com/1/users/profile_image?screen_name="+tusername+"&size=bigger")
            # candidateTags.append({"url" : timagelink.geturl(), "kind" : "twitter"})
            # print str(timagelink.geturl())
            # timagelink.close()
            candidateTags.append({"url": "https://api.twitter.com/1/users/profile_image?screen_name="+tusername+"&size=bigger", "kind": "twitter"})
        print

    print "Twitter icons downloaded!"

    seen = set()
    new_l = []
    for d in candidateTags:
        t = tuple(sorted(d.items()))
        if t not in seen:
            seen.add(t)
            new_l.append(d)
    # print new_l
    candidateTags = new_l  # list(set(candidateTags))

    for candidateTag in candidateTags:
        print candidateTag['kind'], candidateTag['url']
    return candidateTags


def main(argv=None):

    parser = argparse.ArgumentParser(description='Get site avatar and some other data from sites.')
    parser.add_argument('targetUrl', metavar='TARGET_URL',
                        help='The url or domain that you want to get information from')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--avatar', '--images', '-imgs', dest="images", action='store_true',
                       help='shows the list of images/avatar for this url or domain')
    group.add_argument('--facebook-pages', '-fb', dest="facebookPages", action='store_true',
                       help='shows the list of facebook pages/profiles associated with this url or domain')
    group.add_argument('--feeds', dest="feeds", action='store_true',
                       help='shows the list of feeds that can be found in the url or domain')
    group.add_argument('--feed-language', dest="feedLanguage", action='store_true',
                       help='shows the language for the feed URL provided')
    parser.add_argument('--debug', '-d', dest="debug", action='store_true',
                        help='enable debugging mode')

    args = parser.parse_args()

    if argv is None:
        argv = sys.argv

    if args.images:
        candidateTags = getCandidateTags(args.targetUrl)

        print
        print ">>>>>>>>>> Candidates <<<<<<<<<<"
        for candidateTag in candidateTags:
            print candidateTag['kind'], candidateTag['url']
        print ">>>>>>>>> End candidates <<<<<<<"
        print

    if args.facebookPages:
        print "######## facebook pages ########"
        getFacebookPages(args.targetUrl)

    if args.feeds:
        print "######## Feeds urls ########"
        feeds = getFeeds(args.targetUrl, debug=args.debug)
        print "Feed list"
        for feed in feeds:
            print feed['url']

    if args.feedLanguage:
        print "######## Feed language ########"
        print downloadFeedAndGetLanguage(args.targetUrl, args.debug)

    return 0

if __name__ == "__main__":
    sys.exit(main())
