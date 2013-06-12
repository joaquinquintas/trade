from django import template
from django.utils import dateformat

register = template.Library()

class DateRangeNode(template.Node):
    def __init__(self, start_date, end_date, format_string):
        self.start_date = template.Variable(start_date)
        self.end_date = template.Variable(end_date)
        self.format = {}
        if not len(format_string) == 0:
            format_string = format_string.encode('utf-8').strip("\"")
            self.format['day'],self.format['month'],self.format['year'] = format_string.split()
        else:
            self.format['day'],self.format['month'],self.format['year'] = "j","M","Y"
        
    def render(self, context):
        try:
            start_date = self.start_date.resolve(context)
            end_date = self.end_date.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        
        start_format = ""
        end_format = ""

        if end_date:
            if end_date and start_date == end_date :
                start_format = "%s %s, %s" % (self.format['month'], self.format['day'], self.format['year'])
            else :
                start_format = "%s %s" % (self.format['month'], self.format['day'])
                end_format = "%s %s, %s" % (self.format['month'], self.format['day'], self.format['year'])

                if start_date.year != end_date.year:
                    start_format += ", %s" % self.format['year']
        else:
            start_format = "%s %s, %s" % (self.format['month'], self.format['day'], self.format['year'])
                
        ret = dateformat.format(start_date, start_format)
        if end_format:
            ret += " - " + dateformat.format(end_date, end_format)
        return ret


def do_date_range(parser, token):
    """ formats two dates as a date range
    
    eg.
     January 1st 2009 to January 5th 2009 
    would result in:
     1 - 5 January 2009
     
    template usage:
     
     {% date_range start_date end_date [format string] %}
     
     """
    chunks = token.split_contents()
    if not len(chunks) >= 3:
        raise template.TemplateSyntaxError, "%r tag requires two or three arguments" % token.contents.split()[0]
    if not len(chunks) <=4 :
        raise template.TemplateSyntaxError, "%r tag requires two or three arguments" % token.contents.split()[0]
    if len(chunks) == 4:
        format = chunks[3]
    else:
        format = ""
    return DateRangeNode(chunks[1],chunks[2],format)


class TimeRangeNode(template.Node):
    def __init__(self, start_time, end_time, format_string):
        self.start_time = template.Variable(start_time)
        self.end_time = template.Variable(end_time)
        self.format = {}
        if not len(format_string) == 0:
            format_string = format_string.encode('utf-8').strip("\"")
            self.format['hour'],self.format['minute'],self.format['second'] = format_string.split()
        else:
            self.format['hour'],self.format['minute'],self.format['second'] = "g","i",""
        
    def render(self, context):
        start_time, end_time = None, None
        try:
            start_time = self.start_time.resolve(context)
            end_time = self.end_time.resolve(context)
        except template.VariableDoesNotExist:
            pass

        
        if start_time is None:
            return ''
        
        start_format = ""
        end_format = ""

        if start_time == end_time or not end_time:
            start_format = "%s" % self.format['hour']
            if start_time.minute != 0:
                start_format += ":%s" % self.format['minute']
            start_format += " A"
        else:
            start_format = "%s" % self.format['hour']
            if start_time.minute != 0:
                start_format += ":%s" % self.format['minute']

            if end_time:
                end_format = "%s" % self.format['hour']
                if end_time.minute != 0:
                    end_format += ":%s" % self.format['minute']
                end_format += " A"
            else:
                start_format += " A"


        ret = dateformat.time_format(start_time, start_format)
        if end_format:
            ret += " - " + dateformat.time_format(end_time, end_format)
        return ret

def do_time_range(parser, token):
    """ formats two times as a time range
    
    template usage:
     
     {% time_range start_time end_time [format string] %}
     
     """
    chunks = token.split_contents()
    if not len(chunks) >= 3:
        raise template.TemplateSyntaxError, "%r tag requires two or three arguments" % token.contents.split()[0]
    if not len(chunks) <=4 :
        raise template.TemplateSyntaxError, "%r tag requires two or three arguments" % token.contents.split()[0]
    if len(chunks) == 4:
        format = chunks[3]
    else:
        format = ""
    return TimeRangeNode(chunks[1],chunks[2],format)


register.tag('date_range', do_date_range)
register.tag('time_range', do_time_range)
