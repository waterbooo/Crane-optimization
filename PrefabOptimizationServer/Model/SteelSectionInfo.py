from .ModelConstants import ModelConstants

class SteelSectionInfo(object):
    """description of class"""
    def __init__(self, **kwargs):
        self._sectionName = ""
        self._crossSectionalArea = 0.0
        self._plasticSectionModulusX = 0.0
        self._momentOfInertiaX = 0.0
        self._momentOfInertiaY = 0.0
        self._radiusOfGyrationX = 0.0
        self._radiusOfGyrationY = 0.0
        self._topFlangeThickness = 0.0
        self._bottomFlangeThickness = 0.0
        self._webThickness = 0.0
        self._width = 0.0
        self._depth = 0.0

        return super().__init__(**kwargs)

    @property
    def SectionName(self):
        """The name of the section"""
        return self._sectionName

    @SectionName.setter
    def SectionName(self, value):
        self._sectionName = value

    @SectionName.deleter
    def SectionName(self):
        del self._sectionName

    @property
    def CrossSectionalArea(self):
        """Cross-sectional area, A, ft^2"""
        return self._crossSectionalArea

    @CrossSectionalArea.setter
    def CrossSectionalArea(self, value):
        self._crossSectionalArea = value

    @CrossSectionalArea.deleter
    def CrossSectionalArea(self):
        del self._crossSectionalArea

    @property
    def PlasticSectionModulusX(self):
        """Plastic section modulus about the x-axis, Zx, ft^3"""
        return self._plasticSectionModulusX

    @PlasticSectionModulusX.setter
    def PlasticSectionModulusX(self, value):
        self._plasticSectionModulusX = value

    @PlasticSectionModulusX.deleter
    def PlasticSectionModulusX(self):
        del self._plasticSectionModulusX

    @property
    def MomentOfInertiaX(self):
        """Moment of inertia about the x-axis, Ix, ft^4"""
        return self._momentOfInertiaX

    @MomentOfInertiaX.setter
    def MomentOfInertiaX(self, value):
        self._momentOfInertiaX = value

    @MomentOfInertiaX.deleter
    def MomentOfInertiaX(self):
        del self._momentOfInertiaX

    @property
    def MomentOfInertiaY(self):
        """Moment of inertia about the y-axis, Iy, ft^4"""
        return self._momentOfInertiaY

    @MomentOfInertiaY.setter
    def MomentOfInertiaY(self, value):
        self._momentOfInertiaY = value

    @MomentOfInertiaY.deleter
    def MomentOfInertiaY(self):
        del self._momentOfInertiaY

    @property
    def RadiusOfGyrationX(self):
        """Radius of gyration about the x-axis, rx, ft"""
        return self._radiusOfGyrationX

    @RadiusOfGyrationX.setter
    def RadiusOfGyrationX(self, value):
        self._radiusOfGyrationX = value

    @RadiusOfGyrationX.deleter
    def RadiusOfGyrationX(self):
        del self._radiusOfGyrationX

    @property
    def RadiusOfGyrationY(self):
        """Radius of gyration about the y-axis, ry, ft"""
        return self._radiusOfGyrationY

    @RadiusOfGyrationY.setter
    def RadiusOfGyrationY(self, value):
        self._radiusOfGyrationY = value

    @RadiusOfGyrationY.deleter
    def RadiusOfGyrationY(self):
        del self._radiusOfGyrationY

    @property
    def TopFlangeThickness(self):
        """Top flange thickness, tf, ft"""
        return self._topFlangeThickness

    @TopFlangeThickness.setter
    def TopFlangeThickness(self, value):
        self._topFlangeThickness = value

    @TopFlangeThickness.deleter
    def TopFlangeThickness(self):
        del self._topFlangeThickness

    @property
    def BottomFlangeThickness(self):
        """Bottom flange thickness, tf, ft"""
        return self._bottomFlangeThickness

    @BottomFlangeThickness.setter
    def BottomFlangeThickness(self, value):
        self._bottomFlangeThickness = value

    @BottomFlangeThickness.deleter
    def BottomFlangeThickness(self):
        del self._bottomFlangeThickness

    @property
    def WebThickness(self):
        """Web thickness, tw, ft"""
        return self._webThickness

    @WebThickness.setter
    def WebThickness(self, value):
        self._webThickness = value

    @WebThickness.deleter
    def WebThickness(self):
        del self._webThickness

    @property
    def Width(self):
        """Total width, t, ft"""
        return self._width

    @Width.setter
    def Width(self, value):
        self._width = value

    @Width.deleter
    def Width(self):
        del self._width

    @property
    def Depth(self):
        """Total depth, d, ft"""
        return self._depth

    @Depth.setter
    def Depth(self, value):
        self._depth = value

    @Depth.deleter
    def Depth(self):
        del self._depth

    def GetClipsSlots(self, options = None):
        """Forms CLIPS slots for whole section object"""
        slots = " (SectionName \"" + self._sectionName + "\") "
        slots += " (CrossSectionalArea " + str(self._crossSectionalArea) + ") "
        slots += " (PlasticSectionModulusX " + str(self._plasticSectionModulusX) + ") "
        slots += " (MomentOfInertiaX " + str(self._momentOfInertiaX) + ") "
        slots += " (MomentOfInertiaY " + str(self._momentOfInertiaY) + ") "
        slots += " (RadiusOfGyrationX " + str(self._radiusOfGyrationX) + ") "
        slots += " (RadiusOfGyrationY " + str(self._radiusOfGyrationY) + ") "
        slots += " (TopFlangeThickness " + str(self._topFlangeThickness) + ") "
        slots += " (BottomFlangeThickness " + str(self._bottomFlangeThickness) + ") "
        slots += " (WebThickness " + str(self._webThickness) + ") "
        slots += " (Width " + str(self._width) + ") "
        slots += " (Depth " + str(self._depth) + ")"
        return slots

    def GetClipsFacts(self, options = None):
        """Forms CLIPS fact for whole section object"""
        mc = ModelConstants
        fact = ""
        if not options or mc.MappingTagSteelSection in options.Mappings:
            fact = "(SteelSection "
            fact += self.GetClipsSlots(options)
            fact += ")"
        return fact