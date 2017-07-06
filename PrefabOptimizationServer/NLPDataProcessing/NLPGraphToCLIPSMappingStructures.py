import uuid
from .NLPGraphConstants import NLPGraphConstants as gc
from Consts import Strings

from enum import Enum

class BLNlpClipsSlotMap(object):
    """Data for creation a slot in deftamplate construct"""

    def __init__(self, **kwargs):
        self._name = ""
        self._type = ""
        self._default = ""
        self._isIdSlot = False
        self._idOf = ""
        return super().__init__(**kwargs)

    @property
    def Name(self):
        """Slot definition name"""
        return self._name

    @Name.setter
    def Name(self, value):
        self._name = value

    @Name.deleter
    def Name(self):
        del self._name

    @property
    def Type(self):
        """Slot type (e.g. STRING, FLOAT, INTEGER, SYMBOL)"""
        return self._type

    @Type.setter
    def Type(self, value):
        self._type = value

    @Type.deleter
    def Type(self):
        del self._type

    @property
    def Default(self):
        """Slot default value"""
        return self._default

    @Default.setter
    def Default(self, value):
        self._default = value

    @Default.deleter
    def Default(self):
        del self._default

    @property
    def IsIdSlot(self):
        """Indicates whether slot points on another fact by id"""
        return self._isIdSlot

    @IsIdSlot.setter
    def IsIdSlot(self, value):
        self._isIdSlot = value

    @IsIdSlot.deleter
    def IsIdSlot(self):
        del self._isIdSlot

    @property
    def IdOf(self):
        """Deftemplate name of pointed fact"""
        return self._idOf

    @IdOf.setter
    def IdOf(self, value):
        self._idOf = value

    @IdOf.deleter
    def IdOf(self):
        del self._idOf

class BLNlpClipsMultislotMap(object):
    """Data for creation a multislot in deftamplate construct"""

    def __init__(self, **kwargs):
        self._name = ""
        self._type = ""
        self._default = ""
        return super().__init__(**kwargs)

    @property
    def Name(self):
        """Multislot definition name"""
        return self._name

    @Name.setter
    def Name(self, value):
        self._name = value

    @Name.deleter
    def Name(self):
        del self._name

    @property
    def Type(self):
        """Multislot type (e.g. STRING, FLOAT)"""
        return self._type

    @Type.setter
    def Type(self, value):
        self._type = value

    @Type.deleter
    def Type(self):
        del self._type

    @property
    def Default(self):
        """Multislot default value"""
        return self._default

    @Default.setter
    def Default(self, value):
        if not isinstance(value, list):
            self._default = value
        else:
            self._default = ""
            for v in value:
                self._default += str(v)

    @Default.deleter
    def Default(self):
        del self._default

class BLNlpClipsDeftemplateMap(object):
    """Data for creation a deftemplate construct extracted from graph"""

    def __init__(self, **kwargs):
        self._slots = []
        self._multislots = []
        self._templateName = ""
        return super().__init__(**kwargs)

    @property
    def Slots(self):
        """Deftemplate slot definitions"""
        return self._slots

    @Slots.setter
    def Slots(self, value):
        self._slots = value

    @Slots.deleter
    def Slots(self):
        del self._slots

    def AddSlot(self, slot):
        """Adds one slot to template definition"""
        if isinstance(slot, BLNlpClipsSlotMap):
            self._slots.append(slot)
        else:
            s = BLNlpClipsSlotMap()
            if "Name" in slot:
                s.Name = slot["Name"]
                if "Type" in slot:
                    s.Type = slot["Type"]
                if "Default" in slot:
                    s.Default = slot["Default"]
            else:
                s.Name = slot
            self._slots.append(s)

    def GetSlot(self, name):
        """Get a slot object with a specific name"""
        return next((x for x in self._slots if x.Name == name), None)

    def GetIdSlot(self, name):
        """Get a slot object with a specific name + id suffix"""
        return next((x for x in self._slots if x.Name == name + gc.SlotIdSuffix), None)

    @property
    def Multislots(self):
        """Deftemplate multislot definitions"""
        return self._multislots

    @Multislots.setter
    def Multislots(self, value):
        self._multislots = value

    @Multislots.deleter
    def Multislots(self):
        del self._multislots

    def AddMultiSlot(self, slot):
        """Adds single multislot definition to deftemplate"""
        if isinstance(slot, BLNlpClipsMultislotMap):
            self._multislots.append(slot)
        else:
            s = BLNlpClipsMultislotMap()
            if "Name" in slot:
                s.Name = slot["Name"]
                if "Type" in slot:
                    s.Type = slot["Type"]
                if "Default" in slot:
                    s.Default = slot["Default"]
            else:
                s.Name = slot
            self._multislots.append(s)

    def IsMultislot(self, name):
        """check whether slot is a multislot"""
        return next((m for m in self._multislots if m.Name == name), None) != None

    @property
    def TemplateName(self):
        """Name for deftemplate"""
        return self._templateName

    @TemplateName.setter
    def TemplateName(self, value):
        self._templateName = value

    @TemplateName.deleter
    def TemplateName(self):
        del self._templateName

    def ClipsConstruct(self):
        """String representation for deftemplate construct CLIPS code"""
        # Construct definition
        construct = "(deftemplate " + self._templateName + "\n"

        # Slots
        for slot in self._slots:
            construct += "(slot " + slot.Name + ")\n"

        # Multislots
        for multislot in self._multislots:
            construct += "(multislot " + multislot.Name + ")\n"

        # Finish construct
        construct += ")"
        return construct

class BLNlpEnumResultFactRelation(Enum):
    Nothing = 0
    Process = 1
    ProcessStep = 2
    ProcessSubStep = 3

class BLNlpResultingFactProperties(object):
    """Fields related to rule resulting fact mapping"""
    def __init__(self, **kwargs):
        self._elementRelated = False
        self._relatedTo = BLNlpEnumResultFactRelation.Nothing
        return super().__init__(**kwargs)

    @property
    def ElementRelated(self):
        """Indicates whether resulting fact is related to element"""
        return self._elementRelated

    @ElementRelated.setter
    def ElementRelated(self, value):
        self._elementRelated = value

    @ElementRelated.deleter
    def ElementRelated(self):
        del self._elementRelated
    
    @property
    def RelatedTo(self):
        """Indicates whether result is related to Process, process parts or not to anithing enumerated"""
        return self._relatedTo

    @RelatedTo.setter
    def RelatedTo(self, value):
        self._relatedTo = value

    @RelatedTo.deleter
    def RelatedTo(self):
        del self._relatedTo

    def RelatedToStr(self):
        rfre = BLNlpEnumResultFactRelation
        if self._relatedTo == rfre.Nothing:
            return "Nothing"
        elif self._relatedTo == rfre.Process:
            return Strings.ndProcess
        elif self._relatedTo == rfre.ProcessStep:
            return Strings.ndStep
        elif self._relatedTo == rfre.ProcessSubStep:
            return "ProcessSubStep"

class BLNlpClipsFactMap(object):
    """Single fact mapping"""
    def __init__(self, **kwargs):
        self._template = None
        self._slotValues = {}
        self._assert = False
        self._resulting = False
        self._resultingProcess = ""
        self._resultingProperties = BLNlpResultingFactProperties()
        return super().__init__(**kwargs)

    @property
    def Template(self):
        """Defteplate of fact"""
        return self._template

    @Template.setter
    def Template(self, value):
        self._template = value

    @Template.deleter
    def Template(self):
        del self._template

    @property
    def SlotValues(self):
        """Value for each slot in deftemplate"""
        return self._slotValues

    @SlotValues.setter
    def SlotValues(self, value):
        self._slotValues = value

    @SlotValues.deleter
    def SlotValues(self):
        del self._slotValues

    @property
    def Assert(self):
        """Indicates whether this just a fact or an assertion"""
        return self._assert

    @Assert.setter
    def Assert(self, value):
        self._assert = value

    @Assert.deleter
    def Assert(self):
        del self._assert

    @property
    def Resulting(self):
        """Indicates whether this is a result fact, so needs result count binding and two assertions"""
        return self._resulting

    @Resulting.setter
    def Resulting(self, value):
        self._resulting = value

    @Resulting.deleter
    def Resulting(self):
        del self._resulting

    @property
    def ResultingProcess(self):
        """Name of resulting process for produced fact"""
        return self._resultingProcess

    @ResultingProcess.setter
    def ResultingProcess(self, value):
        self._resultingProcess = value

    @ResultingProcess.deleter
    def ResultingProcess(self):
        del self._resultingProcess

    @property
    def ResultingProperties(self):
        """Resulting properties:
               - whether result is element related
               - what process structure is result related to
        """
        return self._resultingProperties

    @ResultingProperties.setter
    def ResultingProperties(self, value):
        self._resultingProperties = value

    @ResultingProperties.deleter
    def ResultingProperties(self):
        del self._resultingProperties

    def ClipsConstruct(self):
        """String representation for fact construct CLIPS code"""
        construct = ""
        # If we have a result assertion fact should have result count binding and two assertions
        if self._assert and self._resulting:
            construct += self.__ResultIdFact()
        
        # Open construct
        construct += "("
        if self._assert:
            construct += "assert ("
        construct += self._template.TemplateName + " "

        if self._assert and self._resulting:
            construct += "(ResultId ?resultId) "

        # Add all slot values
        for (key, value) in self._slotValues.items():
            isMultislot = self.Template.IsMultislot(key)
            multiparts = len(str(value).split(" ")) > 1
            isQuoted = isinstance(value, str) and value[:1] == "\"" and value[-1:] == "\""
            values = []
            if not isMultislot:
                values.append(value)
            else:
                values += value
            if len(values) != 0:
                construct += "(" + key

                for v in values:
                    if not self._assert and multiparts and not isQuoted:
                        construct += " \"" + str(v) + "\" "
                    else:
                        construct += " " + str(v) + " "
                construct += ") "

        # Close construct
        construct += ")"
        if self._assert:
            construct += ")"
        return construct

    def __ResultIdFact(self):
        """String representation of result id fact"""
        construct = "(bind ?resultId (length$ (find-all-facts ((?f  Result)) TRUE)))\n"
        construct += "(assert (Result (Id ?resultId) (ResultTemplate \"" + self._template.TemplateName + "\") (Processes " + self._resultingProcess + ")"
        if self._resultingProperties:
            construct += "(RelatedTo " + self._resultingProperties.RelatedToStr() + ") "
            if self._resultingProperties.ElementRelated:
                construct += "(ElementRelated Yes)"
            
        construct += "))\n"
        return construct


class BLNlpClipsDeffactsMap(object):
    """Set of facts mapping"""
    def __init__(self, **kwargs):
        self._facts = []
        self._name = str(uuid.uuid4())
        return super().__init__(**kwargs)

    @property
    def Facts(self):
        """List if facts in deffacts construct"""
        return self._facts

    @Facts.setter
    def Facts(self, value):
        self._facts = value

    @Facts.deleter
    def Facts(self):
        del self._facts

    def AddFact(self, fact):
        """Adds a single fact to deffacts construct representation"""
        if isinstance(fact, BLNlpClipsFactMap):
            self._facts.append(fact)

    def HasFact(self, name):
        """Checks whether construct contains a specific fact"""
        return next((fact for fact in self._facts if "Id" in fact.SlotValues and fact.SlotValues["Id"] == name), None) != None

    def GetFact(self, name):
        """Gets a specific fact from construct"""
        return next((fact for fact in self._facts if "Id" in fact.SlotValues and fact.SlotValues["Id"] == name), None)

    def ClipsConstruct(self):
        """String representation for deffacts construct CLIPS code"""
        # Open construct
        construct = "(deffacts " + self._name + "\n"

        # Add all facts
        for fact in self._facts:
            construct += fact.ClipsConstruct() + "\n"

        # Close construct
        construct += ")"
        return construct

class BLNlpClipsRuleBase(object):
    """Set of deffacts, deftemplate, defrule, deffunction construct mappings"""
    def __init__(self, **kwargs):
        self._deftemplates = []
        self._deffacts = []
        self._defrules = []
        self._gatheringFunctions = []
        self._predefinedTemplates = []
        __RequirementTemplate = BLNlpClipsDeftemplateMap()
        __RequirementTemplate.TemplateName = "EnumerationResult"
        __RequirementTemplate.AddSlot({"Name": "ResultId"})
        __RequirementTemplate.AddMultiSlot({"Name": "Templates"})
        __RequirementTemplate.AddSlot({"Name": "Name"})
        __RequirementTemplate.AddMultiSlot({"Name": "Variants"})
        self._predefinedTemplates.append(__RequirementTemplate)
        __ResultTemplate = BLNlpClipsDeftemplateMap()
        __ResultTemplate.TemplateName = "Result"
        __ResultTemplate.AddSlot({"Name": "Id"})
        __ResultTemplate.AddSlot({"Name": "ResultTemplate"})
        __ResultTemplate.AddMultiSlot({"Name": "Processes"})
        self._predefinedTemplates.append(__ResultTemplate)
        return super().__init__(**kwargs)

    @property
    def Deftemplates(self):
        """Deftemplate CLIPS construct mappings"""
        return self._deftemplates + self._predefinedTemplates

    @Deftemplates.setter
    def Deftemplates(self, value):
        self._deftemplates = value

    @Deftemplates.deleter
    def Deftemplates(self):
        del self._deftemplates
        del self._predefinedTemplates

    @property
    def PredefDeftemplates(self):
        """Deftemplate CLIPS construct mappings which are predefined"""
        return self._deftemplates + self._predefinedTemplates

    def AddDeftemplate(self, dt):
        """Adds a single deftemplate"""
        if isinstance(dt, BLNlpClipsDeftemplateMap) and self.GetDeftemplate(dt.TemplateName) == None:
            self._deftemplates.append(dt)

    def AddDeftemplates(self, dts):
        """Adds list of deftemplates"""
        if isinstance(dts, list):
            for dt in dts:
                self.AddDeftemplate(dt)

    def GetDeftemplate(self, name):
        """Gets deftemplate construct mapping by name"""
        return next((x for x in self._deftemplates + self._predefinedTemplates if x.TemplateName == name), None)

    @property
    def Deffacts(self):
        """Deffacts CLIPS construct mappings"""
        return self._deffacts

    @Deffacts.setter
    def Deffacts(self, value):
        self._deffacts = value

    @Deffacts.deleter
    def Deffacts(self):
        del self._deffacts

    def AddDeffact(self, df):
        """Adds a single deffacts"""
        if isinstance(df, BLNlpClipsDeffactsMap):
            self._deffacts.append(df)

    def AddDeffacts(self, dfs):
        """Adds list of deffacts"""
        if isinstance(dfs, list):
            for df in dfs:
                self.AddDeffact(df)

    @property
    def Defrules(self):
        """Defrules CLIPS construct mappings"""
        return self._defrules

    @Defrules.setter
    def Defrules(self, value):
        self._defrules = value

    @Defrules.deleter
    def Defrules(self):
        del self._defrules

    def AddDefrule(self, dr):
        """Adds a single defrule"""
        if isinstance(dr, BLNlpClipsDefruleMapping):
            self._defrules.append(dr)

    def AddDefrules(self, drs):
        """Adds list of defrule"""
        if isinstance(drs, list):
            for dr in drs:
                self.AddDefrule(dr)

    @property
    def GatheringFunctions(self):
        """Gathering functions CLIPS construct mappings"""
        return self._gatheringFunctions

    @GatheringFunctions.setter
    def GatheringFunctions(self, value):
        self._gatheringFunctions = value

    @GatheringFunctions.deleter
    def GatheringFunctions(self):
        del self._gatheringFunctions

    def AddGatheringFunction(self, gf):
        """Adds a single gathering function"""
        if isinstance(gf, BLNlpClipsGatheringFunction):
            self._gatheringFunctions.append(gf)

    def AddGatheringFunctions(self, gfs):
        """Adds list of gathering functions"""
        if isinstance(gfs, list):
            for dr in gfs:
                self.AddDefrule(dr)


    def ClipsConstruct(self):
        """String representation for deffacts construct CLIPS code"""
        # Open construct
        construct = ""

        # Add all deftemplates
        for deftemplate in self._deftemplates:
            construct += deftemplate.ClipsConstruct() + "\n"

        # Add all deffacts
        for deffacts in self._deffacts:
            construct += deffacts.ClipsConstruct() + "\n"

        # Add all rules
        for defrule in self._defrules:
            construct += defrule.ClipsConstruct() + "\n"

        # Add all gathering functions
        for gf in self._gatheringFunctions:
            construct += gf.ClipsConstruct() + "\n"
        return construct

class BLNlpClipsRuleCapture(object):
    """Handles information about captured objects for rule"""
    def __init__(self, **kwargs):
        self._deftemplate = None
        self._slot = None
        self._captureName = ""
        self._captureType = "Single"
        self._parent = None
        return super().__init__(**kwargs)

    @property
    def Deftemplate(self):
        """Deftemplate for capture variable from"""
        return self._deftemplate

    @Deftemplate.setter
    def Deftemplate(self, value):
        self._deftemplate = value

    @Deftemplate.deleter
    def Deftemplate(self):
        del self._deftemplate

    @property
    def Slot(self):
        """Slot which is captured"""
        return self._slot

    @Slot.setter
    def Slot(self, value):
        self._slot = value

    @Slot.deleter
    def Slot(self):
        del self._slot

    @property
    def CaptureName(self):
        """Name of variable"""
        return self._captureName

    @CaptureName.setter
    def CaptureName(self, value):
        self._captureName = value

    @CaptureName.deleter
    def CaptureName(self):
        del self._captureName

    @property
    def CaptureType(self):
        """Type of variable (either Single or Multi)"""
        return self._captureType

    @CaptureType.setter
    def CaptureType(self, value):
        self._captureType = value

    @CaptureType.deleter
    def CaptureType(self):
        del self._captureType

    @property
    def Parent(self):
        """Parent capture (variable captured in another template and used for current)"""
        return self._parent

    @Parent.setter
    def Parent(self, value):
        self._parent = value

    @Parent.deleter
    def Parent(self):
        del self._parent

class BLNlpClipsVarBind(object):
    """Handles information about binded objects for rule"""
    def __init__(self, **kwargs):
        self._captureName = ""
        self._value = ""
        return super().__init__(**kwargs)

    @property
    def CaptureName(self):
        """Name of variable"""
        return self._captureName

    @CaptureName.setter
    def CaptureName(self, value):
        self._captureName = value

    @CaptureName.deleter
    def CaptureName(self):
        del self._captureName

    @property
    def Value(self):
        """Value of binding"""
        return self._value

    @Value.setter
    def Value(self, value):
        self._value = value

    @Value.deleter
    def Value(self):
        del self._value

    def ClipsConstruct(self):
        res = "(bind ?" + self.CaptureName + " " + self.Value + ")"
        return res

class BLNlpClipsConditionalVarBind(object):
    """Handles information about binded objects for rule"""
    def __init__(self, **kwargs):
        self._captureName = ""
        self._value = ""
        self._condition = ""
        return super().__init__(**kwargs)

    @property
    def CaptureName(self):
        """Name of variable"""
        return self._captureName

    @CaptureName.setter
    def CaptureName(self, value):
        self._captureName = value

    @CaptureName.deleter
    def CaptureName(self):
        del self._captureName

    @property
    def Value(self):
        """Value of binding"""
        return self._value

    @Value.setter
    def Value(self, value):
        self._value = value

    @Value.deleter
    def Value(self):
        del self._value

    @property
    def Condition(self):
        """Condition of binding"""
        return self._condition

    @Condition.setter
    def Condition(self, value):
        self._condition = value

    @Condition.deleter
    def Condition(self):
        del self._condition

    def ClipsConstruct(self):
        res = "(if " + self._condition + "\n"
        res += "then\n"
        res += "(bind ?" + self.CaptureName + " " + self.Value + "))"
        return res

class BLNlpClipsRuleCondition(object):
    """Single element of defrule conditions part"""
    def __init__(self, **kwargs):

        return super().__init__(**kwargs)

class BLNlpClipsRuleCaptureCondition(BLNlpClipsRuleCondition):
    """Condition capturing elements"""
    def __init__(self, **kwargs):
        self._captures = []
        self._deftemplate = None
        return super().__init__(**kwargs)

    @property
    def Captures(self):
        """Capturing data"""
        return self._captures

    @Captures.setter
    def Captures(self, value):
        self._captures = value

    @Captures.deleter
    def Captures(self):
        del self._captures

    @property
    def Deftemplate(self):
        """Deftemplate base for current captures list"""
        return self._deftemplate

    @Deftemplate.setter
    def Deftemplate(self, value):
        self._deftemplate = value

    @Deftemplate.deleter
    def Deftemplate(self):
        del self._deftemplate

    def ClipsConstruct(self):
        """String representation for rule capturing condition CLIPS code"""
        res = "(" + self._deftemplate.TemplateName + " "
        for capture in self._captures:
            res += "(" + capture.Slot.Name + " ?" + capture.CaptureName + ") "
        res += ")"
        return res

class BLNlpClipsRuleCaptureBasedCondition(BLNlpClipsRuleCondition):
    """Condition using captured elements"""
    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

class BLNlpClipsDefruleMapping(object):
    """Defrule construct mapping"""
    def __init__(self, **kwargs):
        self._inputTemplates = []
        self._conditions = []
        self._outputTemplates = []
        self._outputFacts = []
        self._resolutionBinds = []
        self._name = ""
        self._wholeOutputCondition = ""
        self._priority = 10000
        return super().__init__(**kwargs)

    @property
    def Name(self):
        """Rule name"""
        return self._name

    @Name.setter
    def Name(self, value):
        self._name = value

    @Name.deleter
    def Name(self):
        del self._name

    @property
    def Conditions(self):
        """List of defrule construct conditions
           Each is inherited from BLNlpClipsRuleCondition
        """
        return self._conditions

    @Conditions.setter
    def Conditions(self, value):
        self._conditions = value

    @Conditions.deleter
    def Conditions(self):
        del self._conditions

    def AddCondition(self, cond):
        """Adds a condition to list making sure, that it will be in proper place
           e.g. All captures should go before them are used
        """
        self._conditions.append(cond)

    @property
    def InputTemplates(self):
        """List of defrule construct input templates
           Each is inherited from BLNlpClipsRuleCondition
        """
        return self._inputTemplates

    @InputTemplates.setter
    def InputTemplates(self, value):
        self._inputTemplates = value

    @InputTemplates.deleter
    def InputTemplates(self):
        del self._inputTemplates

    def AddInputTemplate(self, templ):
        """Adds a template to input list"""
        self._inputTemplates.append(templ)

    @property
    def OutputTemplates(self):
        """List of defrule construct output templates
           Each is inherited from BLNlpClipsRuleCondition
        """
        return self._outputTemplates

    @OutputTemplates.setter
    def OutputTemplates(self, value):
        self._outputTemplates = value

    @OutputTemplates.deleter
    def OutputTemplates(self):
        del self._outputTemplates

    def AddOutputTemplate(self, templ):
        """Adds a template to output list"""
        if not templ in self._outputTemplates:
            self._outputTemplates.append(templ)

    @property
    def OutputFacts(self):
        """List of defrule construct output Facts
           Each is inherited from BLNlpClipsRuleCondition
        """
        return self._outputFacts

    @OutputFacts.setter
    def OutputFacts(self, value):
        self._outputFacts = value

    @OutputFacts.deleter
    def OutputFacts(self):
        del self._outputFacts

    def AddOutputFact(self, fact):
        """Adds a fact to outputing list"""
        self._outputFacts.append(fact)

    @property
    def ResolutionBinds(self):
        """List of defrule construct resolution binds
        """
        return self._resolutionBinds

    @ResolutionBinds.setter
    def ResolutionBinds(self, value):
        self._resolutionBinds = value

    @ResolutionBinds.deleter
    def ResolutionBinds(self):
        del self._resolutionBinds

    def AddResolutionBind(self, bind):
        """Adds a bind to list"""
        self._resolutionBinds.append(bind)

    @property
    def WholeOutputCondition(self):
        """List of defrule construct resolution binds
        """
        return self._wholeOutputCondition

    @WholeOutputCondition.setter
    def WholeOutputCondition(self, value):
        self._wholeOutputCondition = value

    @WholeOutputCondition.deleter
    def WholeOutputCondition(self):
        del self._wholeOutputCondition

    @property
    def Priority(self):
        """Rule priority (salience) 
           Range of valid values (-10000; +10000)
        """
        return self._priority

    @Priority.setter
    def Priority(self, value):
        self._priority = value
        if self._priority > 10000:
            self._priority = 10000
        elif self._priority < -10000:
            self._priority = -10000

    @Priority.deleter
    def Priority(self):
        del self._priority

    def ClipsConstruct(self):
        """String representation for defrule construct CLIPS code"""
        name = self._name
        if name == "":
            name = str(uuid.uuid4())
        res = "(defrule " + name + "\n"
        res += "(declare (salience " + str(self._priority) + "))\n"
        for condition in self._conditions:
            res += condition.ClipsConstruct() + "\n"
        res += "=>\n"
        if self._wholeOutputCondition != "":
            res += "(if " + self._wholeOutputCondition + "\n"
            res += "then\n"
        for bind in self._resolutionBinds:
            res += bind.ClipsConstruct() + "\n"
        for fact in self._outputFacts:
            res += fact.ClipsConstruct() + "\n"
        if self._wholeOutputCondition != "":
            res += ")"
        res += ")"
        return res

class BLNlpClipsGatheringFunction(object):
    """Mapping for gathering function"""
    def __init__(self, **kwargs):
        self._deftemplateName = ""
        return super().__init__(**kwargs)

    @property
    def DeftemplateName(self):
        """Deftemplate for gathering name"""
        return self._deftemplateName

    @DeftemplateName.setter
    def DeftemplateName(self, value):
        self._deftemplateName = value

    @DeftemplateName.deleter
    def DeftemplateName(self):
        del self._deftemplateName

    def ClipsConstruct(self):
        """Creates a construct for a gathering function"""
        res = "(deffunction BLGather" + self.DeftemplateName + "s ()\n"
        res += "    (bind ?facts (find-all-facts ((?f " + self.DeftemplateName + ")) TRUE))\n"
        res += ")"
        return res