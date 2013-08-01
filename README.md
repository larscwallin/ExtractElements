ExtractElements
===============

larscwallin.inx.extractelements version 0.1 extracts all selected SVG Elements to file and/or displayed as a string in the 
Inkscape GUI.


UPDATE 130801
* Made some fixes to the SVG output to make it cross browser friendly. Fixes include the addition of the "preserveAspectRatio" attribute to the SVG tag.

UPDATE 130513
* Added a clean up option using the scour.py extension. 

UPDATE 130512
* Moved code from Gist to proper Repo

UPDATE 130510
* Added option to keep the canvas size of the original drawing when exporting. 
     (Previously each exported drawing was sized according to its elements bounding box)
* Bug fixes

UPDATE 130506
* Added movePath method which moves all paths to 0,0 coordinates regardless of their original placement.
* If no elements are selected, the extension now defaults to exporting any visible layers. Precondition for this is that layers have been hidden and then shown again at some point as Inkscape currently does not 
     add meta data by default.

UPDATE 130503
* Added calculation of bounding box and width and height attributes for the resulting SVG doc.
