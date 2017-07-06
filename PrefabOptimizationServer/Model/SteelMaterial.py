import uuid
from .ModelConstants import ModelConstants

class SteelMaterial(object):
    """Material data for steel element"""
    def __init__(self, **kwargs):
        self._name = str(uuid.uuid4())
        self._yeildPoint = 0.0
        self._tensionResistance = 0.0
        self._poissonRatio = 0.0
        self._youngsModulus = 0.0
        return super().__init__(**kwargs)

    @property
    def MaterialName(self):
        """Material name"""
        return self._name

    @MaterialName.setter
    def MaterialName(self, value):
        self._name = value

    @MaterialName.deleter
    def MaterialName(self):
        del self._name

    @property
    def YeildPoint(self):
        """Yeild point"""
        return self._yeildPoint

    @YeildPoint.setter
    def YeildPoint(self, value):
        self._yeildPoint = value

    @YeildPoint.deleter
    def YeildPoint(self):
        del self._yeildPoint

    @property
    def TensionResistance(self):
        """Tension resistance"""
        return self._tensionResistance

    @TensionResistance.setter
    def TensionResistance(self, value):
        self._tensionResistance = value

    @TensionResistance.deleter
    def TensionResistance(self):
        del self._tensionResistance

    @property
    def PoissonRatio(self):
        """Poisson ratio"""
        return self._poissonRatio

    @PoissonRatio.setter
    def PoissonRatio(self, value):
        self._poissonRatio = value

    @PoissonRatio.deleter
    def PoissonRatio(self):
        del self._poissonRatio

    @property
    def YoungsModulus(self):
        """Youngs modulus"""
        return self._youngsModulus

    @YoungsModulus.setter
    def YoungsModulus(self, value):
        self._youngsModulus = value

    @YoungsModulus.deleter
    def YoungsModulus(self):
        del self._youngsModulus

    def GetClipsSlots(self, options = None):
        """Forms CLIPS slots for whole material object"""
        slots = " (MaterialName \"" + self._name + "\") "
        slots += " (YeildPoint " + str(self._yeildPoint) + ") "
        slots += " (TensionResistance " + str(self._tensionResistance) + ") "
        slots += " (PoissonRatio " + str(self._poissonRatio) + ") "
        slots += " (YoungsModulus " + str(self._youngsModulus) + ")"
        return slots

    def GetClipsFacts(self, options = None):
        """Forms CLIPS fact for whole material object"""
        mc = ModelConstants
        fact = ""
        if not options or mc.MappingTagSteelMaterial in options.Mappings:
            fact = "(SteelMaterial "
            fact += self.GetClipsSlots(options)
            fact += ")"
        return fact