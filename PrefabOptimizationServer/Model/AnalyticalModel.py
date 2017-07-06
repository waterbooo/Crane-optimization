from .ModelConstants import ModelConstants
from .BarToElementsRelationships import BarToElementsRelationships

class AnalyticalModel(object):
    """Analytical data about the model"""

    def __init__(self, **kwargs):
        self._bars = {}
        self._barToElementRelationships = {}
        self._barCosts = {}
        self._sections = {}
        self._sectionCosts = {}
        self._materials = {}
        self._materialCosts = {}
        self._beamColumnConnections = {}
        self._FrameSystemType = "SMF"
        self._supportingObjects = {}
        self._curtainWalls = {}
        self._cranePlacementRegions = []
        self._materialDropoffRegions = []
        return super().__init__(**kwargs)

    def AddBarToElementRelationships(self, barToElementRelationships):
        """Adds a bar to elements relahionships mappping to the model"""
        self._barToElementRelationships[barToElementRelationships.BarId] = barToElementRelationships

    def GetBarToElementRelationships(self, barId):
        """Gets bar to elements relationships by bar id"""
        try:
            return self._barToElementRelationships[barId]
        except:
            return BarToElementsRelationships()

    def AddBar(self, bar):
        """Adds a bar to the model"""
        self._bars[bar.Id] = bar

    def GetBar(self, id):
        """Gets bar by id"""
        try:
            return self._bars[id]
        except:
            return None

    @property
    def Bars(self):
        """Bars available in model"""
        return self._bars

    @property
    def Walls(self):
        """Walls available in model"""
        return self._curtainWalls

    @property
    def Panels(self):
        """Panels available in model"""
        panels = {}
        for curtainWall in self._curtainWalls.values():
            panels.update(curtainWall.GetPanels())

        return panels

    @property
    def ConstructionObjects(self):
        """Construction Objects available in model"""
        allObjects = self._bars.copy()
        for curtainWall in self._curtainWalls.values():
            allObjects.update(curtainWall.GetPanels())

        return allObjects

    def AddBeamColumnConnection(self, conn):
        """Adds a beam-column connection to the model"""
        self._beamColumnConnections[conn.Id] = conn

    def GetBeamColumnConnection(self, id):
        """Gets beam-column connection by id"""
        try:
            return self._beamColumnConnections[id]
        except:
            return None

    def AddSection(self, section):
        """Adds a section to the model"""
        self._sections[section.SectionName] = section

    def GetSection(self, name):
        """Gets section by name"""
        try:
            return self._sections[name]
        except:
            return None

    def ContainsSection(self, name):
        """Checks whether section exists in the model"""
        return name in self._sections

    def AddMaterial(self, material):
        """Adds a material to the model"""
        self._materials[material.MaterialName] = material

    def GetMaterial(self, name):
        """Gets material by name"""
        try:
            return self._materials[name]
        except:
            return None

    def ContainsMaterial(self, name):
        """Checks whether material exists in the model"""
        return name in self._materials

    def AddSupportingObject(self, supportingObject):
        """Adds a supporting object (e.g. Plate, Bolt) to the model"""
        self._supportingObjects[supportingObject.Id] = supportingObject

    def GetSupportingObject(self, id):
        """Gets supporting object by id"""
        try:
            return self._supportingObjects[id]
        except:
            return None

    def AddCurtainWall(self, wall):
        """Adds a curatin wall to the model """
        self._curtainWalls[wall.Id] = wall

    def GetCurtainWall(self, id):
        """Gets curatin wall by id"""
        try:
            return self._curtainWalls[id]
        except:
            return None

    def AddCranePlacementRegion(self, polygon):
        """Adds crane placement region to the model"""
        self._cranePlacementRegions.append(polygon)

    def GetCranePlacementRegions(self):
        """Gets all crane placements regions"""
        return self._cranePlacementRegions

    def AddMaterialDropoffRegion(self, polygon):
        """Adds material dropoff region to the model"""
        self._materialDropoffRegions.append(polygon)

    def GetMaterialDropoffRegions(self):
        """Gets all material dropoff regions"""
        return self._materialDropoffRegions

    def GetClipsFacts(self, options=None):
        """Forms CLIPS facts for whole model"""
        mc = ModelConstants
        facts = ""
        for key,bar in self._bars.items():
            facts += bar.GetClipsFacts(options) + "\n"
        for key,relInfo in self._barToElementRelationships.items():
            facts += relInfo.GetClipsFacts(options) + "\n"
        for key,barCost in self._barCosts.items():
            facts += barCost.GetClipsFacts(options) + "\n"
        for key,section in self._sections.items():
            facts += section.GetClipsFacts(options) + "\n"
        for key,sectionCost in self._sectionCosts.items():
            facts += sectionCost.GetClipsFacts(options) + "\n"
        for key,material in self._materials.items():
            facts += material.GetClipsFacts(options) + "\n"
        for key,materialCost in self._materialCosts.items():
            facts += materialCost.GetClipsFacts(options) + "\n"
        for key,conn in self._beamColumnConnections.items():
            facts += conn.GetClipsFacts(options) + "\n"
        if options and mc.MappingTagAnalyticalModel in options.Mappings and mc.MappingModelData in options.Mappings[mc.MappingTagAnalyticalModel]:
            facts += "(ModelData (FrameSystemType " + self._FrameSystemType + "))\n"
        
        return facts
