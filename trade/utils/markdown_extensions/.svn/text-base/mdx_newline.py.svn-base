"""
Newline Markup Extension
===============

This extension modifies markdown's behavior of only inserting html <br> elements when 2 or
more spaces appear at the end of a line.  Instead with this extension loaded, all newlines 
will be converted.

Standard markup only inserts an HTML <br> element when 2 or more spaces appear after a newline
and the next line contains more text.  The reasoning behind this is that when writing in text
one can wrap paragraphs at any point, and this will not insert unwanted newlines into paragraphs.
This behavior works well for composing longer documents in text in which the wrapping should not 
effect the paragraph structure.  However there are times when one might want newlines to always
be converted into html breaks.  For instance users unfamiliar with markdown may be confused by 
the required two spaces.
"""
import markdown, re

LINE_BREAK_RE = r'\n'   # matches end of line

class NewlineExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns["linebreak2"] = \
            markdown.inlinepatterns.SubstituteTagPattern(LINE_BREAK_RE, 'br')

    def reset(self):
        pass

def makeExtension(configs=None) :
    return NewlineExtension()

