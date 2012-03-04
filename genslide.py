#!/usr/bin/env python
#encoding=utf-8
"""
Copyright (c) 2012 huangdx <huangdx@rd.netease.com>
All rights reserved.

Redistribution and use in source and binary forms are permitted
provided that the above copyright notice and this paragraph are
duplicated in all such forms and that any documentation,
advertising materials, and other materials related to such
distribution and use acknowledge that the software was developed
by huangdx.  The name of the
University may not be used to endorse or promote products derived
from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
"""

import os
import sys
import re
import cgi
import zipfile
from htmlentitydefs import name2codepoint
name2codepoint['#39'] = 39

# utils

def usage():
    print 'pys9 - a simple python clone of s9slideshow, yet another html slides generator.'
    print 'usage: python genslides.py'
    print '-o <dir> : output dir, default=./output'
    print '-t <template-path> : template file, default=./template.zip'
    print 'sample: '
    print 'genslide.py < source.md'
    print 'genslide.py -o ./output -t ./template.zip < source.md'

def escape(s):
    return cgi.escape(s, True)

def unescape(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint),
                  lambda m: unichr(name2codepoint[m.group(1)]), s)

def unzip(filename, output_path):
    zfile = zipfile.ZipFile(filename, 'r')
    for p in zfile.namelist():
        zfile.extract(p, output_path)

# end of utils    

def preprocessor(content):
    def hook(s):
        ret = []
        lines = s.split('\n')
        iscode = False
        for line in lines:
            match = re.search('\[code \w+\]', line)
            if iscode is True:
                line = escape(line)
            if match is not None:
                lang = match.group().split(' ')[1][:-1]
                line = line.replace(match.group(), '<div class="code"><pre class="brush: %s toolbar: false gutter: true">' % lang)
                iscode = True
            if '[/code]' in line:
                line = line.replace('[/code]', '</pre></div>')
                iscode = False
            ret.append(line) 
        return '\n'.join(ret)
    
    ret = ''
    slides = content.split('|||')
    for slide in slides:
        slide = '<div class="slide" >'+ render_md(hook(slide)) + '</div>'
        ret += slide
    return ret

def read_md_content(fd):
    try:
        data = fd.readlines()
    except KeyboardInterrupt, e:
        print '\nGoodbye'
        exit(0)

    return ''.join(data)

def render_md(content):
    try:
        import markdown2 as markdown
    except:
        sys.stderr.write('markdown library not found')
        exit(0)
    output = markdown.markdown(content)
    return output

def gen_slides(template_file='template.zip', output = './output', title = 'untitled sildes'):
    try:
        unzip(template_file, output)
        f = open(output + '/index.html','r')
        t = ''.join(f.readlines())

        content = read_md_content(sys.stdin)
        content = preprocessor(content)

        t = t.replace(u'<%content%>', content)
        t = t.replace(u'<%title%>', title)
        f.close()
    
        import codecs
        f = codecs.open(output + "/index.html", "w", "utf-8")
        f.write(t)
        f.close()
    
        return True
    except:
        return False

if __name__ == '__main__':
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:o:n", ["help", "output="])
    except getopt.GetoptError, err:
        print str(err) # will print something like "option -a not recognized"
        sys.exit(2)
    
    template = 'template.zip'
    output = './output'
    title = 'untitled slides'
    for o, a in opts:
        if o in ('-n', '--name'):
            title = a
        elif o in ('-o', '--ouput'):
            output = a
        elif o in ('-t', '--template'):
            template = a
        elif o == '-h':
            usage()
            exit(0)
    
    if gen_slides(template, output, title):
        print 'success'
    else:
        print 'failed'
        exit(3)
