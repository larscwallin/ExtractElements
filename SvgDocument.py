# SvgDocument
# -----------
#
# SVGDocument is a handy wrapper around xml.dom.minidom which allows us
# to quickly build XML structures. It is largely inspired by the SVG class
# of the [svgfig](http://code.google.com/p/svgfig/) project, which was
# used by one of the earlier versions of Kartograph.
#

import base64
import sys
from xml.dom import minidom
from xml.dom.minidom import parse
import re
"""
def main():
    svg = SvgDocument()
    xmlDom = minidom
    xmlDom.Document.appendChild()

    str = svg.toBase64()



    sys.stdout.write(str)
    sys.stdout.flush()

if __name__ == '__main__':
    main()
"""

def _add_attrs(node, attrs):
    for key in attrs:
        node.setAttribute(key.replace('__', '-'), str(attrs[key]))


def _get_label_position(geometry, pos):
    if pos == 'centroid' and not (geometry is None):
        pt = geometry.centroid
        return (pt.x, pt.y)
    else:
        #raise KartographError('unknown label positioning mode ' + pos)
        pass

def _apply_default_label_styles(lg):
    if not lg.getAttribute('font-size'):
        lg.setAttribute('font-size', '12px')
    if not lg.getAttribute('font-family'):
        lg.setAttribute('font-family', 'Arial')
    if not lg.getAttribute('fill'):
        lg.setAttribute('fill', '#000')




class SvgDocument(object):
    # Of course, we need to create and XML document with all this
    # boring SVG header stuff added to it.
    def __init__(self, **kwargs):
        imp = minidom.getDOMImplementation('')
        dt = imp.createDocumentType('svg',
            '-//W3C//DTD SVG 1.1//EN',
            'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd')
        self.doc = imp.createDocument('http://www.w3.org/2000/svg', 'svg', dt)
        self.root = svg = self.doc.getElementsByTagName('svg')[0]
        svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
        svg.setAttribute('version', '1.1')
        svg.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')
        _add_attrs(self.root, kwargs)
        return None

    # This is the magic of SvgDocument. Instead of having to do appendChild()
    # and addAttribute() for every node we create, we just call svgdoc.node()
    # which is smart enough to append itself to the parent if we specify one,
    # and also sets all attributes we pass as keyword arguments.
    def node(self, name, parent=None, **kwargs):
        el = self.doc.createElement(name)

        _add_attrs(el, kwargs)
        if parent is not None:
            parent.appendChild(el)
        return el


    # This is the magic of SvgDocument. Instead of having to do appendChild()
    # and addAttribute() for every node we create, we just call svgdoc.node()
    # which is smart enough to append itself to the parent if we specify one,
    # and also sets all attributes we pass as keyword arguments.
    def nodeFromObject(self, name, parent=None, **kwargs):
        el = self.doc.createElement(name)
        _add_attrs(el, kwargs)
        if parent is not None:
            parent.appendChild(el)
        return el


    # Sometimes we also need a <[CDATA]> block, for instance if we embed
    # CSS code in the SVG document.
    def cdata(self, data, parent=None):
        cd = minidom.CDATASection()
        cd.data = data
        if parent is not None:
            parent.appendChild(cd)
        return cd

    # Here we finally write the SVG file, and we're brave enough
    # to try to write it in Unicode.
    def write(self, outfile, pretty_print=False):
        if isinstance(outfile, (str, unicode)):
            outfile = open(outfile, 'w')
        if pretty_print:
            raw = self.doc.toprettyxml('utf-8')
        else:
            raw = self.doc.toxml('utf-8')
        try:
            raw = raw.encode('utf-8')
        except:
            #print 'warning: could not encode to unicode'
            pass

        outfile.write(raw)
        outfile.close()

    # Don't blame me if you don't have a command-line shortcut to
    # simply the best free browser of the world.
    def preview(self, command, pretty_print=False):
        import tempfile
        tmpfile = tempfile.NamedTemporaryFile(suffix='.svg', delete=False)
        self.write(tmpfile, pretty_print)
        #print 'map stored to', tmpfile.name
        from subprocess import call
        call([command, tmpfile.name])

    def toString(self, pretty_print=False):
        if pretty_print:
            return self.doc.toprettyxml()
        return self.doc.toxml()

    def toBase64(self):
        docSource = ''
        docSource = self.doc.toxml()
        encStr = base64.b64encode(docSource.encode())
        return encStr

    def fromBase64(self, encStr):
        pass

    # This is an artifact of an older version of Kartograph, but
    # maybe we'll need it later. It will load an SVG document from
    # a file.
    @staticmethod
    def load(filename):
        svg = SvgDocument()
        dom = parse(filename)
        svg.doc = dom
        svg.root = dom.getElementsByTagName('svg')[0]
        return svg

