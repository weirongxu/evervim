#!/usr/bin/env python
# encoding: utf-8
# vim: sts=4 sw=4 fdm=marker
# Author: kakkyz <kakkyz81@gmail.com>
# License: MIT
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
import markdownAndENML
from evernoteapi import EvernoteAPI
import markdown
import unittest
from xml.dom import minidom

class TestMarkdownAndENML(unittest.TestCase):
    """ doc """

    def setUp(self):  # {{{
        pass
    #}}}

    def _getMarkdownSample(self, fname): # {{{
        fp = open('markdownAndENML_test/'+fname, 'r')
        cont = fp.read()
        fp.close()
        return cont
    # }}}

    def _getXmlSample(self, fname): # {{{
        fp = open('markdownAndENML_test/'+fname, 'r')
        cont = fp.read()
        fp.close()
        return cont
    # }}}

    def _writeTemp(self, cont, fname='temp.md'): # {{{
        fp = open('markdownAndENML_test/'+fname, 'w')
        fp.write(cont)
        fp.close()
    # }}}

    # def testParseMarkdown(self): # {{{
    #     parsedContent = markdownAndENML.parseMarkdown(self._getMarkdownSample())
    #     content = EvernoteAPI.NOTECONTENT_HEADER + parsedContent.encode('utf-8') + EvernoteAPI.NOTECONTENT_FOOTER
    #     lines = content.decode('utf8').splitlines()
    #     # lines = markdown.markdown(self._getMarkdownSample().decode('utf-8')).splitlines()
    #     for i, l in enumerate(self._getXmlSample().splitlines()):
    #         # print u"{0} , {1}".format(lines[i], l.decode('utf8'))
    #         self.assertEqual(lines[i], l.decode('utf8'),
    #                 "\nline: {0}\n{1}\n{2}".format(i+1, repr(lines[i]), repr(l.decode('utf8'))))
    #}}}

    def testParseENML(self):  # {{{
        sampleXML = self._getXmlSample('ENML_src.html')
        doc = minidom.parseString(sampleXML)
        ennote = doc.getElementsByTagName("en-note")[0]
        lines = markdownAndENML.parseENML(ennote).splitlines()
        self._writeTemp("\n".join(lines).encode('utf8'))
        try:
            for i, l in enumerate(self._getMarkdownSample('ENML_tar.md').splitlines()):
                self.assertEqual(lines[i], l.decode('utf8'))
        except Exception as e:
            msg = u"\n# line: {0}\n- {1}\n- {2}".format(
                    i+1, lines[i], l.decode('utf8'))
            print(msg)
            self.fail(msg)
    # }}}


if __name__ == '__main__':
    from time import localtime, strftime
    print '\n**' + strftime("%a, %d %b %Y %H:%M:%S", localtime()) + '**\n'
# profileを取るとき
#   import test.pystone
#   import cProfile
#   import pstats
#   prof = cProfile.run("unittest.main()", 'cprof.prof')
#   p = pstats.Stats('cprof.prof')
#   p.strip_dirs()
#   p.sort_stats('cumulative')
#   p.print_stats()
#
# 全て流す時
    unittest.main()
#
# 個別でテストするとき
#   suite = unittest.TestSuite()
#   suite.addTest(TestMarkdownAndENML('testParseENML'))
#   unittest.TextTestRunner().run(suite)
