# -*- coding: utf-8 -*-

# This can't be executable otherwise nosetests won't work
import unittest
from nose.tools import ok_, nottest
from fabicon import getCandidateTags
import os


def genResEntry(kind, url):
    return {"kind": kind, "url": url}


def resultsAreEqual(url, resultList1, expectedList2):
    resultSet1 = set([(d['kind'], d['url']) for d in resultList1])
    expectedSet2 = set([(d['kind'], d['url']) for d in expectedList2])

    for d in expectedSet2:
        ok_(d in resultSet1, str(d)+" was expected, but could not be found in results")

    for d in resultSet1:
        ok_(d in expectedSet2, str(d)+" is not among expected results")


class TestKnownWebsites():
    knownResults = (
        ("http://globo.com", "globo_com.txt",
         [genResEntry("apple", "http://s.glbimg.com/en/ho/static/touchphone/img/apple-touch-icon-iphone.png"),
          genResEntry("apple", "http://s.glbimg.com/en/ho/static/touchphone/img/apple-touch-icon-ipad.png"),
          genResEntry("apple", "http://s.glbimg.com/en/ho/static/touchphone/img/apple-touch-icon-iphone-retina.png"),
          genResEntry("openGraph", "http://s.glbimg.com/en/ho/static/globocom2012/img/gcom_marca_og.jpg")]),
        ("http://uol.com.br", "uol_com_br.txt",
         [genResEntry("image_src", "http://img.uol.com.br/image_src/uol.gif"),
          genResEntry("apple", "http://h.imguol.com/icon-touch.png")]),
        ("http://www.eternosprazeres.com", "eternosprazeres_com.txt",
         [genResEntry("facebook", "https://graph.facebook.com/100002962630949/picture?type=normal"),
          genResEntry("facebook", "https://graph.facebook.com/100002962630949/picture?width=150&height=150"),
          genResEntry("facebook", "https://graph.facebook.com/100002962630949/picture?width=500")]),
        ("http://www.blogdasaude.com.br", "blogdasaude_com_br.txt",
         [genResEntry("apple", "http://www.blogdasaude.com.br/wp-content/themes/blogdasaude/images/icone_blog_ipad.png"),
          genResEntry("facebook", "https://graph.facebook.com/205963512747817/picture?type=normal"),
          genResEntry("facebook", "https://graph.facebook.com/205963512747817/picture?width=150&height=150"),
          genResEntry("facebook", "https://graph.facebook.com/205963512747817/picture?width=500"),
          genResEntry("twitter", "https://api.twitter.com/1/users/profile_image?screen_name=blogdasaude&size=original"),
          genResEntry("twitter", "https://api.twitter.com/1/users/profile_image?screen_name=blogdasaude&size=bigger")]),
        ("http://gamesreflexoes.blogspot.com.br", "gamesreflexoes_blogspot_com_br.txt",
         [genResEntry("facebook", "https://graph.facebook.com/212611295424933/picture?type=normal"),
          genResEntry("facebook", "https://graph.facebook.com/212611295424933/picture?width=150&height=150"),
          genResEntry("facebook", "https://graph.facebook.com/212611295424933/picture?width=500"),
          genResEntry("facebook", "https://graph.facebook.com/100000343727632/picture?type=normal"),
          genResEntry("facebook", "https://graph.facebook.com/100000343727632/picture?width=150&height=150"),
          genResEntry("facebook", "https://graph.facebook.com/100000343727632/picture?width=500"),
          genResEntry("twitter", "https://api.twitter.com/1/users/profile_image?screen_name=gamesreflexoes&size=original"),
          genResEntry("twitter", "https://api.twitter.com/1/users/profile_image?screen_name=gamesreflexoes&size=bigger")]),
        ("http://terra.com.br", "terra_com_br.txt",
         [genResEntry("apple", "http://s1.trrsf.com.br/opera.jpg")]),
        ("http://tudogostoso.uol.com.br", "tudogostoso_uol_com_br.txt",
         [genResEntry("facebook", "https://graph.facebook.com/tudogostoso/picture?type=normal"),
          genResEntry("facebook", "https://graph.facebook.com/tudogostoso/picture?width=150&height=150"),
          genResEntry("facebook", "https://graph.facebook.com/tudogostoso/picture?width=500"),
          genResEntry("twitter", "https://api.twitter.com/1/users/profile_image?screen_name=tudo_gostoso&size=original"),
          genResEntry("twitter", "https://api.twitter.com/1/users/profile_image?screen_name=tudo_gostoso&size=bigger")])
    )

    def resultsAreEqual(self, url, resultList1, expectedList2):
        resultSet1 = set([(d['kind'], d['url']) for d in resultList1])
        expectedSet2 = set([(d['kind'], d['url']) for d in expectedList2])

        for d in expectedSet2:
            ok_(d in resultSet1, str(d)+" was expected, but could not be found in results")

        for d in resultSet1:
            ok_(d in expectedSet2, str(d)+" is not among expected results")

    def testCandidateTags(self):
        for url, htmlFile, expectedResult in self.knownResults:

            resultsAreEqual.description = 'getCandidateTags give expected results for %s' % url

            script_full_path = os.path.realpath(__file__)
            script_dir = os.path.dirname(script_full_path)
            f = open(script_dir + "/resources/statichtml/"+htmlFile, 'r')
            staticHtml = f.read()

            candidateTags = getCandidateTags(url, staticHtml=staticHtml)

            yield resultsAreEqual, url, candidateTags, expectedResult

    # def testBadFormatedHtml(self):
          # Tuple to treat really bad html (crazy comments like <!- ->) (regular expression, replacement function)
          # Examples
          # www.zupi.com.br has <!– fim da id logo –> --> it is not - it is –


if __name__ == "__main__":
    import nose
    nose.main()
