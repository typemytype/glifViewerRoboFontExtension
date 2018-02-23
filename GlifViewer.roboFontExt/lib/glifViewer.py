from AppKit import *
import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.events import addObserver, removeObserver

from mojo.roboFont import version

if version >= "3.0.0":
    from ufoLib.glifLib import writeGlyphToString, readGlyphFromString
else:
    from robofab.glifLib import writeGlyphToString, readGlyphFromString

from defcon.objects.glyph import addRepresentationFactory

from lib.scripting.codeEditor import CodeEditor

from mojo.roboFont import CurrentGlyph, OpenWindow, RGlyph


def PlistFactory(glyph, font):
    return writeGlyphToString(glyph.name, glyph, glyph.drawPoints)

addRepresentationFactory("com.typemytype.GlyphXMLViewer", PlistFactory)

class GlyphXMLViewer(BaseWindowController):

    def __init__(self):
        self.currentGlyph = None
        self.w = vanilla.Window((500, 500), "Plist Viewer", minSize=(100, 100))
        self.w.xml = CodeEditor((0, 0, -0, -30), "", lexer="xml")

        self.w.applyButton = vanilla.Button((-70, -25, -20, 22), "Apply", callback=self.applyCallback, sizeStyle="small")
        addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
        self.setUpBaseWindowBehavior()

        self.currentGlyphChanged({})

        self.w.open()

    def windowCloseCallback(self, sender):
        self._unsubscribeGlyph()
        removeObserver(self, "currentGlyphChanged")
        super(GlyphXMLViewer, self).windowCloseCallback(sender)

    def applyCallback(self, sender):
        if self.currentGlyph is not None:
            xml = self.w.xml.get()

            dummyGlyph = RGlyph()
            try:
                readGlyphFromString(str(xml), dummyGlyph, dummyGlyph.getPointPen())
            except:
                import traceback
                error = "A problem occured when trying to parse the glif plist."
                suggestion = traceback.format_exc(5)
                self.showMessage(error, suggestion)
                return

            self.currentGlyph.clear()
            readGlyphFromString(str(xml), self.currentGlyph, self.currentGlyph.getPointPen())

    def setXML(self):
        if self.currentGlyph is not None:
            xml = self.currentGlyph.naked().getRepresentation("com.typemytype.GlyphXMLViewer")
            self.w.xml.set(xml)

    def currentGlyphChanged(self, info):
        glyph = CurrentGlyph()

        if glyph == self.currentGlyph:
            return
        self._unsubscribeGlyph()
        if glyph is not None:
            self.subscribeGlyph(glyph)
            self.currentGlyph = glyph
            self.setXML()
        else:
            self.w.xml.set("")

    def _unsubscribeGlyph(self):
        if self.currentGlyph is not None:
            self.currentGlyph.removeObserver(self, "Glyph.Changed")
            self.currentGlyph = None

    def subscribeGlyph(self, glyph):
        if glyph is not None:
            glyph.addObserver(self, "_glyphChanged", "Glyph.Changed")

    def _glyphChanged(self, notification):
        self.setXML()

OpenWindow(GlyphXMLViewer)
