#!/usr/bin/env python
# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
import base64
import string
import webbrowser
import threading
import os.path
import math
import re
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
                    <svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="100%" height="100%" viewBox="0 0 {{element.width}} {{element.height}}" xml:space="preserve" preserveAspectRatio="xMinYMin">
                    <style/>
                    {{element.source}}
                    {{js}}
                    </svg>"""

    cssTemplate = """.{{css.prefix}}{{element.label}}{{css.suffix}}:url({{element.source}});"""
    sassTemplate = """${{sass.var.prefix}}{{element.label}}{{sass.var.suffix}}="{{element.source}}";"""
    js = """<script><![CDATA[(function(){if(document.location.hash){var d=[],e,c,g=!1,b="",f=!1;location.href.split("?")[1].split("&").forEach(function(a){rule=a.split("=");key=rule[0];val=rule[1];"id"!=key?(f=!0,d.push(rule)):c=val});f&&(e=c?document.getElementById(c):document.getElementsByTagName("svg")[0])&&(d.forEach(function(a){2==a.length&&(val=a[1],(g=/(^#[0-9A-F]{6}$)|(^#[0-9A-F]{3}$)/i.test(val))&&(b+=a[0]+":"+val+";"))}),""!==b&&e.setAttribute("style",b))}})();]]></script>"""

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

        self.OptionParser.add_option('--includejs', action = 'store',
              type = 'inkbool', dest = 'includejs', default = False,
              help = 'Include Javascript to support ?color=hexvalue parameter?')

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
        self.renderSass = True
        self.includeJS = self.options.includejs
        self.CSSSource = []

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

            # Iterate through all selected elements
            for element in self.selected:

                elementLabel = str(element.get(inkex.addNS('label', 'inkscape'),''))
                elementId = element.get('id')

                if(elementLabel != ''):
                    element.set('label',elementLabel)
                    element.set('class',elementLabel)
                else:
                    pass

                tagName= self.getTagName(element)

                if(tagName == 'path'):
                    # Paths can easily be moved by recalculating their d attributes
                    if(self.reposition or self.resizeDrawing):
                        pathData = self.movePath(element,0,0,'tl')
                        if(pathData):
                            element.set('d',pathData)

                elif(tagName == 'g'):
                    # Groups however are best "transformed" into place using translate
                    # self.translateElement(element,0,0,False)
                    pass

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
                    if(self.includeJS):
                        tplResult = string.replace(tplResult,'{{js}}',self.js)
                    else:
                        tplResult = string.replace(tplResult,'{{js}}','')

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

                        if(self.renderSass):
                            content = ('$data-url-'+label+':"data:image/svg+xml;name='+label+';base64,'+(base64.b64encode(content))+'";')
                            #node['source'] = ('data:image/svg+xml;name='+label+';base64,'+(base64.b64encode(content)))
                            #content = self.renderSassStyle(node)
                        else:
                            pass
                            #content = ('data:image/svg+xml;name='+label+';base64,'+(base64.b64encode(content)))

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

    def renderCSS(source):
        pass
        #if(source):
            #self.CSSSource = (self.CSSSource + '')

    def renderSassStyle(source):
        if(source):
            self.CSSSource = (self.CSSSource + '')

    def getTagName(self,node):
        type = node.get(inkex.addNS('type', 'sodipodi'))

        if(type == None):
            #remove namespace data {....}
            tagName= node.tag
            tagName= tagName.split('}')[1]
        else:
            tagName= str(type)

        return tagName

    # Move element using transform translate
    def translateElement(self,node,x,y,relative = False):

        # Grab transform attribute if it exists.
        transform = node.get('transform','')

        # Compute the nodes bounding box
        box =list(simpletransform.computeBBox([node]))

        pos_x = box[0]
        pos_y = box[2]

        # rotation center is not a breeze to calculate from the matrix, so thanks inkscape ;)
        origin_x = float(node.get(inkex.addNS('transform-center-x', 'inkscape'),0))
        origin_y = float(node.get(inkex.addNS('transform-center-y', 'inkscape'),0))
        origin_x = origin_x + ( box[1] / 2)
        origin_y = (origin_y * -1) + ( box[3] / 2)

        if(transform==''):
            # If there is no transform attribute on the node we add one
            node.attrib['transform'] = ''

        # simpletransform returns a multi dim array of matrix values
        transform = simpletransform.parseTransform(transform)

        transformObject = self.normalizeMatrix(transform)
        inkex.debug(transformObject)
        #offset_x = (transform[0][2]-pos_x)
        #offset_y = (transform[1][2]-pos_y)
        offset_x = (pos_x * -1)
        offset_y = (pos_y * -1)

        inkex.debug([offset_x,offset_y])

        transform = simpletransform.parseTransform(('translate(' + str(offset_x) + ' ' + str(offset_y) + ')'),transform)

        transformObject = self.normalizeMatrix(transform)
        inkex.debug(transformObject)

        inkex.debug(transform)

        if(relative == False):
            matrix = simpletransform.formatTransform(transform)
            node.set('transform',matrix)
            inkex.debug(matrix)
        else:
            simpletransform.applyTransformToNode(transform,node)


    def parseStyleAttribute(self,str):

        #inkex.debug(self.debug_tab + 'Got style ' + str)

        rules = str.split(';')
        parsed_set = {}
        result = ''
        for rule in rules:
            parts = rule.split(':')

            if(len(parts) > 1):

                key = self.camelConvert(parts[0])
                val = self.camelConvert(parts[1])

                if(key== 'filter'):
                    parsed_set['filter'] = self.parseFilter(val)
                elif(key == 'fill' and val.find('url(#') > -1):
                    parsed_set['fillGradient'] = self.parseGradient(val)
                elif(key == 'stroke' and val.find('url(#') > -1):
                    parsed_set['strokeGradient'] = self.parseGradient(val)
                else:
                    parsed_set[key] = val

        return parsed_set

    def expandMatrix(self,normalizedMatrix):
        pass

    def normalizeMatrix(self,matrix):
      degree = 180 / math.pi
      radian = math.pi / 180

      a = matrix[0][0]
      b = matrix[1][0]
      c = matrix[0][1]
      d = matrix[1][1]
      tx = matrix[0][2]
      ty = matrix[1][2]

      scaleX = math.sqrt((a * a) + (c * c))
      scaleY = math.sqrt((b * b) + (d * d))

      sign = math.atan(-c / a)
      rad  = math.acos(a / scaleX)
      deg  = rad * degree
      reflectX = (a < 0)
      reflectY = (d < 0)

      if (deg > 90 and sign > 0):
        rotation = (360 - deg) * radian

      elif (deg < 90 and sign < 0):
        rotation = (360 - deg) * radian
      else:
        rotation = rad

      rotationInDegree = rotation * degree

      # If we have a reflected matrix we subtract 180 degrees
      if(reflectX or reflectY):
        rotationInDegree = (rotationInDegree - 180)
        rotation = (rotation - math.pi)

      if(reflectX):
        scaleX = (scaleX * -1)
      if(reflectY):
        scaleY = (scaleY * -1)


      return {
        'scale':{
          'x':scaleX,
          'y':scaleY
        },
        'rotate':{
          'degree':rotationInDegree,
          'radiance':rotation
        },
        'reflect':{
            'x':str(reflectX),
            'y':str(reflectY)
        },
        'translate':{
          'x':tx,
          'y':ty
        },
        'matrix':matrix
    }

    def matrixToList(self, matrix):
        """
        From matrix order,

        1          3           5         2          4          6

        to  sequencial list

        1          2           3          4          5         6
        """

        return [
            matrix[0][0],
            matrix[1][0],
            matrix[0][1],
            matrix[1][1],
            matrix[0][2],
            matrix[1][2]
        ]


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
