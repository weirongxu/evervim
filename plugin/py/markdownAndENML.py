# encoding: utf-8
# vim: sts=4 sw=4 fdm=marker
# Author: kakkyz <kakkyz81@gmail.com>
# License: MIT
import markdown
import xml.sax.saxutils
import re

# TODO: use vim indent length?
__INDENT__ = 4 * " "

class parserOption:  # {{{
    def __init__(self):
        self.a          = False
        self.ul         = 0
        self.ol         = 0
        self.li         = 0
        self.pre        = False
        self.code       = False
        self.p          = False
        self.blockquote = 0
        self.listCount = 0

    def __str__(self):
        return "a={0} ul={1} ol={2} li={3} pre={4} code={5} p={6} blockquote={7} listCount={8} ".format(
                self.a,
                self.ul,
                self.ol,
                self.li,
                self.pre,
                self.code,
                self.p,
                self.blockquote,
                self.listCount)
#}}}

removeheadercode = re.compile('^<code>')
removefootercode = re.compile('</code>$')


def parseENML(node, level=0, result='', option=parserOption()):  # {{{
# import html2text
#   return html2text.html2text(node.toxml())
#   print node.toxml()
#   print "{0}:{1}:{2}:{3}:{4}:{5}".format(
#           level ,
#           _getNodeType(node) ,
#           _getTagName(node),
#           _getAttribute(node),
#           _getData(node), option)
    if node.nodeType == node.ELEMENT_NODE:
        tag = _getTagName(node)
        if tag == "en-note":
            for child in node.childNodes:
                if child.nodeType == node.ELEMENT_NODE:
                    # Partition block
                    if len(result) == 0 or result[-2:] == '\n\n':
                        pass
                    elif result[-1:] == '\n':
                        result += '\n'
                    else:
                        result += '\n\n'
                    result += parseENML(child, level + 1, "", option) + '\n'
                elif node.nodeType == node.TEXT_NODE:
                    result += parseENML(child, level + 1, "", option)
        elif tag == "a":
            htmlhref = _getAttribute(node)
            option.a = True
            htmltext = "".join([parseENML(child, level + 1, "", option) for child in node.childNodes])
            option.a = False
#           result += '[{0}]({1})'.format(htmltext, htmlhref) # this code does not work multibyte!
            result += '[{' + htmltext + '}]({' + htmlhref + '})'
        elif tag == "pre":
            option.pre = True
            result += "".join([parseENML(child, level + 1, result, option) for child in node.childNodes])
            option.pre = False
        elif tag == "code":
            option.code = True
            if option.pre == True:
                # precode = removeheadercode.sub('', xml.sax.saxutils.unescape(node.toxml()))
                precode = removeheadercode.sub('', _unescape(node.toxml()))
                precode = removefootercode.sub('', precode)
                for line in precode.splitlines():
                    result += __INDENT__ + "%s\n" % line.rstrip()
                result += "\n"
            else:
                # incode = removeheadercode.sub('`', xml.sax.saxutils.unescape(node.toxml()))
                incode = removeheadercode.sub('`', _unescape(node.toxml()))
                incode = removefootercode.sub('`', incode)
                result += incode
            option.code = False
        elif tag == "p":
            option.p = True
            result += "".join([parseENML(child, level + 1, "", option) for child in node.childNodes])
            result = re.compile(r'<br/?>').sub('  ', result)
            result += '\n'
            option.p = False
        elif tag == "ul":
            option.ul += 1
            option.listCount = 0
            result += "".join([parseENML(child, level + 1, "", option) for child in node.childNodes])
            # print "'"+result+"'"
            option.ul -= 1
        elif tag == "ol":
            option.ol += 1
            option.listCount = 0
            result += "".join([parseENML(child, level + 1, "", option) for child in node.childNodes])
            option.ol -= 1
        elif tag == "li":
            option.li += 1
            option.listCount += 1
            listCount = option.listCount

            indent = __INDENT__ * (option.li - 1)
            if _getTagName(node.parentNode) == 'ul':
                result += indent + "* "
            elif _getTagName(node.parentNode) == 'ol':
                result += indent + str(option.listCount) + ". "

            for child in node.childNodes:
                cont = parseENML(child, level + 1, '', option)
                if cont.strip():
                    if child.nodeType == node.ELEMENT_NODE \
                            and _getTagName(child) in ['ul', 'ol']:
                        if result[-1] != '\n':
                            result += '\n'
                    else:
                        # ['strong', 'em']
                        if result[-1] != ' ':
                            result += ' '
                    result += cont
            if result[-1] != '\n':
                result += '\n'
            option.listCount = listCount
            option.li -= 1
        elif tag == "strong":
            result = "".join([parseENML(child, level + 1, "", option) for child in node.childNodes])
            result = '**' + result + '**'
        elif tag == "em":
            result = "".join([parseENML(child, level + 1, "", option) for child in node.childNodes])
            result = '_' + result + '_'
        elif tag in ["img", "br", "en-media", "en-todo", "en-crypt"]:  # 後で改行を除去して見やすくする？
            result += node.toxml()
            result += "\n"
        elif tag == "blockquote":
            option.blockquote += 1
            result += "".join([parseENML(child, level + 1, "", option) for child in node.childNodes])
            result = "\n".join(['> ' + line for line in result[:-1].split("\n")]) + "\n"
            option.blockquote -= 1
            if level == 0:
                result += "\n"
        elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            headerlv = tag[1:]
            result += ("#" * int(headerlv)) + " " + "".join([parseENML(child, level + 1, "", option) for child in node.childNodes])
        else:
            result += "".join([parseENML(child, level + 1, result, option) for child in node.childNodes])
    elif node.nodeType == node.TEXT_NODE:
        text = _getData(node)
        if text:
            result += text
        if not option.pre:
            result = _clearNeedlessSpace(result)
    return result
#}}}


def parseMarkdown(mkdtext):  # {{{
    m = markdown.markdown(mkdtext.decode('utf-8'))
    return m
#}}}

# ----- private methods


def _getTagName(node):  # {{{
    if node.nodeType == node.ELEMENT_NODE:
        return node.tagName
    return None
#}}}


def _getData(node):  # {{{
    """ return textdata """
    if node.nodeType == node.TEXT_NODE:
        return node.data.strip()
    return ""
#}}}

def _unescape(text): # {{{
    import HTMLParser
    return HTMLParser.HTMLParser().unescape(text)
#}}}

def _clearNeedlessSpace(text):
    text = re.compile(r'[ \t]*\n[ \t]*').sub('\n', text)
    return re.compile(r'[ \t]+').sub(' ', text)

def _getAttribute(node):  # {{{
    try:
        if _getTagName(node) == "a":
            return node.getAttribute("href")
    except:
        pass
    return None
#}}}


def _getNodeType(node):  # {{{
    """ return NodeType as String """
    if   node.nodeType == node.ELEMENT_NODE                    : return   "ELEMENT_NODE"
    elif node.nodeType == node.ATTRIBUTE_NODE                  : return   "ATTRIBUTE_NODE"
    elif node.nodeType == node.TEXT_NODE                       : return   "TEXT_NODE"
    elif node.nodeType == node.CDATA_SECTION_NODE              : return   "CDATA_SECTION_NODE"
    elif node.nodeType == node.ENTITY_NODE                     : return   "ENTITY_NODE"
    elif node.nodeType == node.PROCESSING_INSTRUCTION_NODE     : return   "PROCESSING_INSTRUCTION_NODE"
    elif node.nodeType == node.COMMENT_NODE                    : return   "COMMENT_NODE"
    elif node.nodeType == node.DOCUMENT_NODE                   : return   "DOCUMENT_NODE"
    elif node.nodeType == node.DOCUMENT_TYPE_NODE              : return   "DOCUMENT_TYPE_NODE"
    elif node.nodeType == node.NOTATION_NODE                   : return   "NOTATION_NODE"
    return "UKNOWN NODE"
#}}}

if __name__ == "__main__":
    import doctest
    doctest.testmod()
