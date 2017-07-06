class BarToElementsRelationships(object):
    """description of class"""
    def __init__(self, **kwargs):
        self._barId = ""
        self._connections = []
        self._attachedElements = []
        self._relatedNonAttachedElements = []
        self._isAttached = False
        self._isAttachedTo = ""
        self._isGrouped = False
        self._groupId = ""
        self._assemblyNumber = 0
        self._isOnGroundColumn = False
        return super().__init__(**kwargs)

    @property
    def BarId(self):
        """Identifier of bar"""
        return self._barId

    @BarId.setter
    def BarId(self, value):
        self._barId = value

    @BarId.deleter
    def BarId(self):
        del self._barId

    @property
    def Connections(self):
        """Ids of bars connected with current one"""
        return self._connections

    @Connections.setter
    def Connections(self, value):
        self._connections = value

    @Connections.deleter
    def Connections(self):
        del self._connections

    @property
    def AttachedElements(self):
        """Ids of elements which are lifted together with current bar"""
        return self._attachedElements

    @AttachedElements.setter
    def AttachedElements(self, value):
        self._attachedElements = value

    @AttachedElements.deleter
    def AttachedElements(self):
        del self._attachedElements

    @property
    def RelatedNonAttachedElements(self):
        """Ids of elements connected to bar in final state but not lifted together with it"""
        return self._relatedNonAttachedElements

    @RelatedNonAttachedElements.setter
    def RelatedNonAttachedElements(self, value):
        self._relatedNonAttachedElements = value

    @RelatedNonAttachedElements.deleter
    def RelatedNonAttachedElements(self):
        del self._relatedNonAttachedElements

    @property
    def IsAttached(self):
        """Indicates whether bar is attached to another one and is lifted together with it"""
        return self._isAttached

    @IsAttached.setter
    def IsAttached(self, value):
        self._isAttached = value

    @IsAttached.deleter
    def IsAttached(self):
        del self._isAttached

    @property
    def IsAttachedTo(self):
        """The id of bar which current one is attached to"""
        return self._isAttachedTo

    @IsAttachedTo.setter
    def IsAttachedTo(self, value):
        self._isAttachedTo = value

    @IsAttachedTo.deleter
    def IsAttachedTo(self):
        del self._isAttachedTo

    @property
    def IsGrouped(self):
        """Indicates whether bar is a part of group
           e.g. a part of a larger construction item which is delivered and lifted as a solid one
        """
        return self._isGrouped

    @IsGrouped.setter
    def IsGrouped(self, value):
        self._isGrouped = value

    @IsGrouped.deleter
    def IsGrouped(self):
        del self._isGrouped

    @property
    def GroupId(self):
        """The id of group current bar is a part of"""
        return self._groupId

    @GroupId.setter
    def GroupId(self, value):
        self._groupId = value

    @GroupId.deleter
    def GroupId(self):
        del self._groupId

    @property
    def AssemblyNumber(self):
        """Assembly number from e.g. Advance Steel"""
        return self._assemblyNumber

    @AssemblyNumber.setter
    def AssemblyNumber(self, value):
        self._assemblyNumber = value

    @AssemblyNumber.deleter
    def AssemblyNumber(self):
        del self._assemblyNumber

    @property
    def IsOnGroundColumn(self):
        """Assembly number from e.g. Advance Steel"""
        return self._isOnGroundColumn

    @IsOnGroundColumn.setter
    def IsOnGroundColumn(self, value):
        self._isOnGroundColumn = value

    @IsOnGroundColumn.deleter
    def IsOnGroundColumn(self):
        del self._isOnGroundColumn

    def __GetBarConnectionSlots(self, cId):
        """Forms slots for two bars connection mark"""
        slots = " (BarId1 " + self.BarId + ") "
        slots += " (BarId2 " + cId + ")"
        return slots

    def __GetBarConnectionFact(self, cId):
        """Forms fact for two bars connection mark"""
        fact = "(BarsConnected "
        fact += self.__GetBarConnectionSlots(cId)
        fact += ")"
        return fact

    def __GetBarConnectionFacts(self):
        """Forms all facts for two bars connection marks through the model"""
        facts = ""
        for barId in self.Connections:
            facts += self.__GetBarConnectionFact(barId) + "\n"
        return facts

    def __GetBarAttachedSlots(self, elId):
        """Forms slots for bar and element attached mark"""
        slots = " (BarId " + self.BarId + ") "
        slots += " (Element " + elId + ")"
        return slots
    
    def __GetBarAttachedFact(self, elId):
        """Forms fact for bar and element attached mark"""
        fact = "(AttachedElement "
        fact += self.__GetBarAttachedSlots(elId)
        fact += ")"
        return fact

    def __GetBarAttachedFacts(self):
        """Forms facts for bar and element attached marks through the model"""
        facts = ""
        for elId in self.AttachedElements:
            facts += self.__GetBarAttachedFact(elId) + "\n"
        return facts

    def __GetBarRelatedSlots(self, elId):
        """Forms slots for bar and element relation mark"""
        slots = " (BarId " + self.BarId + ") "
        slots += " (Element " + elId + ")"
        return slots
    
    def __GetBarRelatedFact(self, elId):
        """Forms fact for bar and element relation mark"""
        fact = "(RelatedNonAttachedElement "
        fact += self.__GetBarRelatedSlots(elId)
        fact += ")"
        return fact

    def __GetBarRelatedFacts(self):
        """Forms facts for bar and element relation marks through the model"""
        facts = ""
        for elId in self.RelatedNonAttachedElements:
            facts += self.__GetBarRelatedFact(elId) + "\n"
        return facts

    def __GetBarGroupSlots(self, groupId):
        """Forms slots for bar in group mark"""
        slots = " (BarId " + self.BarId + ") "
        slots += " (Group " + groupId + ")"
        return slots
    
    def __GetBarGroupFact(self, groupId):
        """Forms fact for bar in group mark"""
        fact = "(BarGroupedIn "
        fact += self.__GetBarRelatedSlots(groupId)
        fact += ")"
        return fact

    def __GetBarGroupFacts(self):
        """Forms facts for bar in group marks through the model"""
        facts = ""
        if self.IsGrouped:
            facts = self.__GetBarGroupFact(self.GroupId)
        return facts

    def GetClipsFacts(self, options=None):
        """Forms all Relationships facts through the model"""
        facts = ""
        facts += self.__GetBarConnectionFacts() + "\n"
        facts += self.__GetBarAttachedFacts() + "\n"
        facts += self.__GetBarRelatedFacts() + "\n"
        facts += self.__GetBarGroupFacts() + "\n"
        return facts
