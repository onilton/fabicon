import bottle
import urllib
from bottle import route, run, template, request, static_file
from bottle import debug, response
import fabicon
import json

from bottle import SimpleTemplate 
SimpleTemplate.defaults["get_url"] =  bottle.default_app().get_url
#SimpleTemplate.defaults["base_url"] = "/favicon" 

@route('/<filepath:path>', name='static_root' )
def server_static(filepath):
    return static_file(filepath, root='.')

@route('/',method='GET', name='index')
def fabicon_demo():
    url = request.GET.get('url', '').strip() 

    print "Site name",fabicon.getName(url)

    exampleUrls=["http://uol.com.br",
	"http://terra.com.br",
	"http://tudogostoso.uol.com.br",
	"http://www.csmonitor.com",
	"http://www.folha.uol.com.br/tec/",
	"http://adrenaline.com.br/",
	"http://nokia.com.br"]
    exampleSites=[]
    for exampleUrl in exampleUrls:
	    exampleSites.append({"url": exampleUrl, "urlencoded":urllib.quote(exampleUrl, ''), "name": fabicon.getName(exampleUrl) })
    urlencoded=urllib.quote(url, '')
    output = template('main', { "url" : url , "urlencoded" : urlencoded, "exampleSites" : exampleSites})

    return output

@route('/icons',method='GET', name="icons")
def simple_request():
    url = request.GET.get('url', '').strip() 
    if url!="":
	    candidateTags=fabicon.getCandidateTags(url)
	    output = template('icons', { "candidateTags" : candidateTags, "url" : url})
    
    return output


@route('/json',method='GET', name="json")
def json_request():
    url = request.GET.get('url', '').strip() 
    if url!="":
	    candidateTags=fabicon.getCandidateTags(url)
	    output = json.dumps({ "url" : url, "candidateTags" : candidateTags}, sort_keys=True, indent=4)
    
    return output


@route('/feedsjson',method='GET', name="feedsjson")
def feedjson_request():
    url = request.GET.get('url', '').strip() 
    if url!="":
	    feedUrls=fabicon.getFeeds(url)
	    output = json.dumps({ "url" : url, "feedUrls" : feedUrls}, sort_keys=True, indent=4)

    return output

@route('/fbpagesjson',method='GET', name="fbpagesjson")
def fbpagesjson_request():
    url = request.GET.get('url', '').strip() 
    if url!="":
	    facebookPages=fabicon.getFacebookPages(url)
	    output = json.dumps({ "url" : url, "facebookPages" : facebookPages}, sort_keys=True, indent=4)

    response.headers['Access-Control-Allow-Origin'] = '*'
    return output

