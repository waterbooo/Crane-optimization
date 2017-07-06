from Consts import *

class NLPGraphConstants(object):
    """Contains all constants related to knowledge graph obtained from NLP processing"""

    # Relations used to find root objects (objects from which parsing starts)
    RootRelations = [Strings.is_, Strings.has, Strings.part]

    # Meaningful relations for object parsing
    ParseObjectRelationIds = [Strings.is_, Strings.has, Strings.part, Strings.in_, Strings.after, Strings.input, Strings.tool]

    # Capture identifiers
    CaptureSingle = "Single"
    CaptureMulti = "Multi"
    BindedVariablePref = "BindedVariable" 

    CaptureSourceDelimiter = "->"

    # Filtered relations group names
    InputRelations = "in"
    OutgoingRelations = "out"

    # Node markers
    EnumerateRequirements = "EnumerateRequirements"

    # Requirement markers
    RequirementFor = "For"

    # ================CLIPS================
    SlotIdSuffix = "Id"
    CaptureIdBody = "Id"
    StrCat = "str-cat"
    Equal = "eq"
    NotEqual = "neq"

    # Result template names
    TemplateResult = "Result"
    TemplateEnumerationResult = "EnumerationResult"

    #=====================Regexes============
    ClipsVariablesInGraphDescription = "[%][?]\w+"
    SimpleCondition = "[%]([?]\w+\s{0,}={2}.+)[?](.+)[:](.+)"
    SingleComparison = "([?]\w+)\s{0,}([<>=!]+)\s{0,}(.+)"