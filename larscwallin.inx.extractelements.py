#!/usr/bin/env python
# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
import base64
import string
import webbrowser
import threading
import os.path

sys.path.append('/usr/share/inkscape/extensions')

import SvgDocument
import inkex
import simpletransform
import simplepath
import simplestyle
from scour import scourString

class ExtractElements(inkex.Effect):

    exportTemplate = """<?xml version="1.0" standalone="no"?>
                    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
                    "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                    <svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{{element.width}}" height="{{element.height}}">
                    {{element.source}}
                    </svg>"""

    def __init__(self):
        """
        Constructor.
        Defines the "--what" option of a script.
        """
        # Call the base class constructor.
        inkex.Effect.__init__(self)

        self.OptionParser.add_option('-w', '--where', action = 'store',
          type = 'string', dest = 'where', default = '',
          help = '')

        self.OptionParser.add_option('--encode', action = 'store',
              type = 'inkbool', dest = 'encode', default = False,
              help = 'Base64 encode the result?')

        self.OptionParser.add_option('--viewresult', action = 'store',
              type = 'inkbool', dest = 'viewresult', default = False,
              help = 'View resulting?')

        self.OptionParser.add_option('--resize', action = 'store',
              type = 'inkbool', dest = 'resize', default = False,
              help = 'Resize the drawing canvas to the elements?')

        self.OptionParser.add_option('--reposition', action = 'store',
              type = 'inkbool', dest = 'reposition', default = False,
              help = 'Reposition elements to the top left corner of the drawing?')

        self.OptionParser.add_option('--scour', action = 'store',
              type = 'inkbool', dest = 'scour', default = False,
              help = 'Clean up drawing source using Scour?')



    def effect(self):
        """
        Effect behaviour.
        """
        self.where = self.options.where
        self.base64Encode = self.options.encode
        self.viewResult = self.options.viewresult
        self.resizeDrawing = self.options.resize
        self.reposition = self.options.reposition
        self.scour = self.options.scour

        self.getselected()

        self.svgDoc = self.document.xpath('//svg:svg',namespaces=inkex.NSS)[0]
        self.svgWidth  = inkex.unittouu(self.svgDoc.get('width'))
        self.svgHeight  = inkex.unittouu(self.svgDoc.get('height'))

        overideElementDim = False

        # Temporary solution where I grab all defs, regardless of if they are actually used or not
        # defs = self.document.xpath('//svg:svg/svg:defs',namespaces=inkex.NSS)[0]

        layers = self.document.xpath('//svg:svg/svg:g[@style!="display:none"]',namespaces=inkex.NSS)

        """
        if(len(defs) > 0):
            defs = inkex.etree.tostring(defs)
        else:
            defs = '<defs/>'
        """


        # If no elements where selected we default to exporting every visible layer in the drawing
        if(self.selected.__len__() <= 0):
            self.selected = layers
            # As we are exporting whole layers we assume that the resulting SVG drawings has the
            # same dimensions as the source document and thus overide the elements bounding box.
            overideElementDim = True
        else:
            self.selected = self.selected.values()

        if(self.selected.__len__() > 0):
            selected = []

            # Iterate through all elements
            for element in self.selected:

                elementLabel = str(element.get(inkex.addNS('label', 'inkscape'),''))
                elementId = element.get('id')

                tagName= self.getTagName(element)

                if(tagName== 'path'):

                    if(self.reposition or self.resizeDrawing):
                        pathData = self.movePath(element,0,0,'tl')
                        if(pathData):
                            element.set('d',pathData)

                elementBox = list(simpletransform.computeBBox([element]))
                elementBox[1] = (elementBox[1]-elementBox[0])
                elementBox[3] = (elementBox[3]-elementBox[2])

                if(overideElementDim == False):
                    elementWidth = elementBox[1]
                    elementHeight = elementBox[3]
                else:
                    elementWidth = self.svgWidth
                    elementHeight = self.svgHeight

                elementSource = inkex.etree.tostring(element)

                if(elementSource!=''):
                    # Wrap the node in an SVG doc
                    if(self.resizeDrawing):
                        tplResult = string.replace(self.exportTemplate,'{{element.width}}',str(elementWidth))
                        tplResult = string.replace(tplResult,'{{element.height}}',str(elementHeight))
                    else:
                        tplResult = string.replace(self.exportTemplate,'{{element.width}}',str(self.svgWidth))
                        tplResult = string.replace(tplResult,'{{element.height}}',str(self.svgHeight))

                    #tplResult = string.replace(tplResult,'{{document.defs}}',defs)
                    tplResult = string.replace(tplResult,'{{element.source}}',elementSource)

                    if(self.scour):
                        tplResult = self.scourDoc(tplResult)

                    # If the result of the operation is valid, add the SVG source to the selected array
                    if(tplResult):
                        selected.append({
                            'id':elementId,
                            'label':elementLabel,
                            'source':tplResult,
                            'box':elementBox
                            })

            for node in selected:
                # Cache these in local vars
                content = node['source']
                id = node['id']
                label = node['label'] or node['id']

                if(content!=''):

                    if(self.base64Encode):
                        content = ('data:image/svg+xml;name='+label+';base64,'+(base64.b64encode(content)))

                    if(self.where!=''):

                        # The easiest way to name rendered elements is by using their id since we can trust that this is always unique.
                        filename = os.path.join(self.where, (id+'-'+label+'.svg'))
                        success = self.saveToFile(content,filename)

                        if(success):
                            if(self.viewResult):
                                self.viewOutput(filename)
                        else:
                            inkex.debug('Unable to write to file "' + filename + '"')

                    else:
                        if(self.viewResult):
                            if(self.base64Encode):
                                inkex.debug(content)
                                inkex.debug('')
                                #self.viewOutput('data:image/svg+xml;base64,'+content)
                            else:
                                inkex.debug(content)
                                inkex.debug('')
                                #self.viewOutput('data:image/svg+xml,'+content)
                        else:
                            inkex.debug(content)

                else:
                    inkex.debug('No SVG source available for element ' + id)
        else:
                inkex.debug('No SVG elements or layers to extract.')


    def getTagName(self,node):
        type = node.get(inkex.addNS('type', 'sodipodi'))

        if(type == None):
            #remove namespace data {....}
            tagName= node.tag
            tagName= tagName.split('}')[1]
        else:
            tagName= str(type)

        return tagName


    def movePath(self,node,x,y,origin):
        tagName= self.getTagName(node)

        if(tagName!= 'path'):
            inkex.debug('movePath only works on SVG Path elements. Argument was of type "' + tagName+ '"')
            return False

        path = simplepath.parsePath(node.get('d'))
        id = node.get('id')

        box = list(simpletransform.computeBBox([node]))

        offset_x = (box[0] - x)
        offset_y = (box[2] - (y))

        for cmd in path:
            params = cmd[1]
            i = 0

            while(i < len(params)):
                if(i % 2 == 0):
                    #inkex.debug('x point at ' + str( round( params[i] )))
                    params[i] = (params[i] - offset_x)
                    #inkex.debug('moved to ' + str( round( params[i] )))
                else:
                    #inkex.debug('y point at ' + str( round( params[i]) ))
                    params[i] = (params[i] - offset_y)
                    #inkex.debug('moved to ' + str( round( params[i] )))
                i = i + 1

        return simplepath.formatPath(path)

    def scourDoc(self,str):
        return scourString(str).encode("UTF-8")

    def saveToFile(self,content,filename):

        FILE = open(filename,'w')

        if(FILE):
            FILE.write(content)
            FILE.close()
            return True
        else:
            return False

    def viewOutput(self,url):
        runner = BrowserRunner()
        runner.url = url
        runner.start()

class BrowserRunner(threading.Thread):
    url = ''
    def __init__(self):
        threading.Thread.__init__ (self)

    def run(self):
        webbrowser.open('file://' + self.url)

# Create effect instance and apply it.
effect = ExtractElements()
effect.affect(output=False)

#inkex.errormsg(_("This will be written to Python stderr"))
