#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import unittest
import fabicon
from fabicon import getCandidateTags



def genResEntry(kind, url):
	return { "kind" : kind, "url" : url}

class TestKnownWebsites(unittest.TestCase):                          
    knownResults = ( ("http://globo.com", "globo_com.txt", 
				[ genResEntry("apple", "http://s.glbimg.com/en/ho/static/touchphone/img/apple-touch-icon-iphone.png"),
				  genResEntry("apple", "http://s.glbimg.com/en/ho/static/touchphone/img/apple-touch-icon-ipad.png"),
				  genResEntry("apple", "http://s.glbimg.com/en/ho/static/touchphone/img/apple-touch-icon-iphone-retina.png"),
				  genResEntry("openGraph", "http://s.glbimg.com/en/ho/static/globocom2012/img/gcom_marca_og.jpg" ) ]),
                     ("http://uol.com.br", "uol_com_br.txt",
				[ genResEntry("image_src", "http://img.uol.com.br/image_src/uol.gif"),
				  genResEntry("apple","http://h.imguol.com/icon-touch.png") ]),
                     ("http://tudogostoso.uol.com.br", "tudogostoso_uol_com_br.txt",
				[ genResEntry("facebook", "https://graph.facebook.com/tudogostoso/picture?type=normal"),
				  genResEntry("facebook", "https://graph.facebook.com/tudogostoso/picture?width=150&height=150"),
				  genResEntry("facebook", "https://graph.facebook.com/tudogostoso/picture?width=500"),
				  genResEntry("twitter", "https://api.twitter.com/1/users/profile_image?screen_name=tudo_gostoso&size=original"),
				  genResEntry("twitter", "https://api.twitter.com/1/users/profile_image?screen_name=tudo_gostoso&size=bigger") ] ) )                       

    def resultsAreEqual(self,resultList1, expectedList2):
        resultSet1 = set([(d['kind'], d['url']) for d in resultList1])
        expectedSet2 = set([(d['kind'], d['url']) for d in expectedList2])
        #return [d for d in list1 if (d['classname'], d['testname']) not in check]
        #return set1 == set2


	for d in expectedSet2:
		self.assertTrue(d in resultSet1, str(d)+" was expected, but could not be found in results")                  

	for d in resultSet1:
		self.assertTrue(d in expectedSet2, str(d)+" is not among expected results")                  

	
    def testCandidateTags(self):                          

        """getCandidateTags should give known result with known input"""
        for url, htmlFile, expectedResult in self.knownResults:              
	    #print "ULR === ",url
	    f = open("resources/statichtml/"+htmlFile, 'r')
	    staticHtml = f.read()

	    candidateTags = getCandidateTags(url,staticHtml=staticHtml)


    	    self.resultsAreEqual(candidateTags, expectedResult)

	    #set1 = set([(d['kind'], d['url']) for d in expectedResult])
	    #set2 = set([(d['kind'], d['url']) for d in candidateTags])
#		for candidateTag in candidateTags:
#			print candidateTag['kind'],candidateTag['url']
            #result = roman.toRoman(integer)                    
            #self.assertEqual(set1, set2)                  

#    def testFromRomanKnownValues(self):                          
#        """fromRoman should give known result with known input"""
#        for integer, numeral in self.knownValues:                
#            result = roman.fromRoman(numeral)                    
#            self.assertEqual(integer, result)                    
#
#class ToRomanBadInput(unittest.TestCase):                            
#    def testTooLarge(self):                                          
#        """toRoman should fail with large input"""                   
#        self.assertRaises(roman.OutOfRangeError, roman.toRoman, 4000)
#
#    def testZero(self):                                              
#        """toRoman should fail with 0 input"""                       
#        self.assertRaises(roman.OutOfRangeError, roman.toRoman, 0)   
#
#    def testNegative(self):                                          
#        """toRoman should fail with negative input"""                
#        self.assertRaises(roman.OutOfRangeError, roman.toRoman, -1)  
#
#    def testNonInteger(self):                                        
#        """toRoman should fail with non-integer input"""             
#        self.assertRaises(roman.NotIntegerError, roman.toRoman, 0.5) 
#
#class FromRomanBadInput(unittest.TestCase):                                      
#    def testTooManyRepeatedNumerals(self):                                       
#        """fromRoman should fail with too many repeated numerals"""              
#        for s in ('MMMM', 'DD', 'CCCC', 'LL', 'XXXX', 'VV', 'IIII'):             
#            self.assertRaises(roman.InvalidRomanNumeralError, roman.fromRoman, s)
#
#    def testRepeatedPairs(self):                                                 
#        """fromRoman should fail with repeated pairs of numerals"""              
#        for s in ('CMCM', 'CDCD', 'XCXC', 'XLXL', 'IXIX', 'IVIV'):               
#            self.assertRaises(roman.InvalidRomanNumeralError, roman.fromRoman, s)
#
#    def testMalformedAntecedent(self):                                           
#        """fromRoman should fail with malformed antecedents"""                   
#        for s in ('IIMXCC', 'VX', 'DCM', 'CMM', 'IXIV',
#                  'MCMC', 'XCX', 'IVI', 'LM', 'LD', 'LC'):                       
#            self.assertRaises(roman.InvalidRomanNumeralError, roman.fromRoman, s)
#
#class SanityCheck(unittest.TestCase):        
#    def testSanity(self):                    
#        """fromRoman(toRoman(n))==n for all n"""
#        for integer in range(1, 4000):       
#            numeral = roman.toRoman(integer) 
#            result = roman.fromRoman(numeral)
#            self.assertEqual(integer, result)
#
#class CaseCheck(unittest.TestCase):                   
#    def testToRomanCase(self):                        
#        """toRoman should always return uppercase"""  
#        for integer in range(1, 4000):                
#            numeral = roman.toRoman(integer)          
#            self.assertEqual(numeral, numeral.upper())
#
#    def testFromRomanCase(self):                      
#        """fromRoman should only accept uppercase input"""
#        for integer in range(1, 4000):                
#            numeral = roman.toRoman(integer)          
#            roman.fromRoman(numeral.upper())          
#            self.assertRaises(roman.InvalidRomanNumeralError,
#                              roman.fromRoman, numeral.lower())
#

	

#https://api.twitter.com/1/users/profile_image?screen_name=motorclube&size=bigger



#def main(argv=None):
#
#	parser = argparse.ArgumentParser(description='Get site avatar and some other data from sites.')
#	parser.add_argument('targetUrl', metavar='TARGET_URL', 
#			help='The url or domain that you want to get information from')
#	group = parser.add_mutually_exclusive_group()
#	group.add_argument('--avatar', '--images', '-imgs', dest="images", action='store_true', 
#			help='shows the list of images/avatar for this url or domain')
#	group.add_argument('--facebook-pages', '-fb', dest="facebookPages", action='store_true',
#			help='shows the list of facebook pages/profiles associated with this url or domain')
#	group.add_argument('--feeds', dest="feeds", action='store_true',
#			help='shows the list of feeds that can be found in the url or domain')
#	group.add_argument('--feed-language', dest="feedLanguage", action='store_true',
#			help='shows the language for the feed URL provided')
#	parser.add_argument('--debug','-d', dest="debug", action='store_true',
#			help='enable debugging mode')
#
#	args = parser.parse_args()
#
#	if argv is None:
#		argv = sys.argv
#	#print argv[1]
#	
#
#
#	if args.images:
#		candidateTags = getCandidateTags(args.targetUrl)
#		#candidateTags = getCandidateTags(sys.argv[1])
#
#		print
#		print ">>>>>>>>>> Candidates <<<<<<<<<<"
#		for candidateTag in candidateTags:
#			print candidateTag['kind'],candidateTag['url']
#		print ">>>>>>>>> End candidates <<<<<<<"
#		print
#
#
#	if args.facebookPages:
#		print "######## facebook pages ########"
#		#getFacebookPages(sys.argv[1])
#		getFacebookPages(args.targetUrl)
#
#
#
#	if args.feeds:
#		print "######## Feeds urls ########"
#		#feeds = getFeeds(sys.argv[1])
#		feeds = getFeeds(args.targetUrl, debug=args.debug)
#		print "Feed list"
#		for feed in feeds:
#			print feed['url']
#
#
#	if args.feedLanguage:
#		print "######## Feed language ########"
#		print downloadFeedAndGetLanguage(args.targetUrl, args.debug)
#
#	return 0

if __name__ == "__main__":
	unittest.main()
    #sys.exit(main())



