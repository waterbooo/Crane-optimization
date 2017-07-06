import networkx as nx
from .NLPGraphToCLIPSMappingStructures import *
from .NLPGraphConstants import NLPGraphConstants as gc
from .NLPGraphProcessingUtils import NLPGraphProcessingUtils as ngutils
import re, uuid
from Consts import *

class NLPResultGraphParser(object):
    """Parser for graph result of NLP text processing
       Takes networkx graph as input structure and produces a set of CLIPS rule files.
    """

    def ParseGraph(self, G):
        """Parses graph into a set of deftemplate, deffacts, defrule and deffunction constructs representation"""
        # Create resulting object
        res = BLNlpClipsRuleBase()

        # The most important relations for deffacts and deftemplates
        rels = gc.RootRelations
        
        # Get root nodes: nodes without input relations or without at least relations from rels list
        roots = []
        for n in G.nodes():
            inEdges = G.in_edges([n], data = True)
            if len(inEdges) == 0:
                roots.append(n)
            else:
                # If there are input relations check for relations from rels list
                hasForbiddenIn = False
                for edge in inEdges:
                    if Strings.rel in edge[2] and edge[2][Strings.rel] in rels:
                        hasForbiddenIn = True
                        break
                if not hasForbiddenIn:
                    roots.append(n)

        # Do graph search starting from root nodes
        seen = []
        for root in roots:
            self.ParseObject(G, root, seen, res)

        # Parse gathering functions
        self.GetGatheringFunctions(G, res)

        # Priritize the rules
        self.GetRulePriorities(G, res)
            
        # Return parsed constructs
        return res
        
    def ParseObject(self, G, node, seen, results):
        """Parses object node
           G: networkx DiGraph
           node: node with object definition
           returns: deftemplate or deffacts object for CLIPS
        """
        # List of relations to look for
        meaningfulRelationIds = gc.ParseObjectRelationIds

        # Get all relations which are meaningful for us
        relations = self.GetInOutRelationsForList(G, node, meaningfulRelationIds)

        # Proceed the relations
        if len(relations[gc.OutgoingRelations][Strings.is_]) > 0:
            if len(relations[gc.InputRelations][Strings.is_]) > 0:
                # deftemplate
                if not node in seen:
                    self.ParseDeftemplate(G, node, relations, seen, results) 
            elif len(relations[gc.InputRelations][Strings.has]) == 0:
                # deffacts
                if not Strings.attrRuleOut in G.node[node]:
                    valRelations = self.GetValRelations(G, node)
                    self.ParseDeffact(G, node, relations, valRelations, seen, results)
                else:
                    # Parse deftemplates even for resulting facts
                    for rel in relations[gc.OutgoingRelations][Strings.is_]:
                        self.ParseObject(G, rel[1], seen, results)

                    # This is rule result, parse rule from it
                    self.ParseDefrule(G, node, seen, results)
            else:
                # slot with id
                return self.ParseIdSlot(G, node, relations, seen, results)
        elif len(relations[gc.InputRelations][Strings.is_]) > 0 or len(relations[gc.OutgoingRelations][Strings.has]) > 0:
            # deftemplate
            if not node in seen:
                self.ParseDeftemplate(G, node, relations, seen, results)
        elif len(relations[gc.InputRelations][Strings.has]) > 0:
            # slot
            seen.append(node)
            return self.ParseSlot(G, node)

    def ParseSlot(self, G, node):
        """Parses slot definition from node"""
        slot = BLNlpClipsSlotMap()
        slot.Name = node
        return slot

    def ParseIdSlot(self, G, node, relations, seen, results):
        """Parses a node definition, which represents id of another object and a template for object it is pointing on (if it is not parsed yet)
           returns: slot(s)
        """
        slots = []
        templates = []
        
        # Get all leading definition relations
        outIsRelations = relations[gc.OutgoingRelations][Strings.is_]

        # Construct id slot items from got relations
        for isRel in outIsRelations:
            slot = BLNlpClipsSlotMap()
            slot.IsIdSlot = True
            slot.Name = node + gc.SlotIdSuffix
            slot.IdOf = isRel[1]
            slots.append(slot)
            seen.append(node)

            # If there is no deftemplate for relation target yet, define one
            if not isRel[1] in seen:
                self.ParseObject(G, isRel[1], seen, results)
                seen.append(isRel[1])
        return slots

    def ParseAggregationSlot(self, G, node, relations, seen, results):
        """Parses a node definition, which points on aggregator id and a template for aggregator (if it is not parsed yet)
           example: ProcessStep is aggregated into Process
                    ProcessId slot will be created
           returns: slot
        """
        slots = []
        templates = []

        # Get leading definition and aggregation relations
        outIsRelations = relations[gc.OutgoingRelations][Strings.is_]
        outPartRelations = relations[gc.OutgoingRelations][Strings.part]

        # Construct id pointing slots for aggregation relations
        for partRel in outPartRelations:
            slot = BLNlpClipsSlotMap()
            slot.IsIdSlot = True
            slot.Name = partRel[1] + gc.SlotIdSuffix
            slot.IdOf = partRel[1]
            slots.append(slot)

            # Construct deftemplate for aggregator if there is no one
            if not partRel[1] in seen:
                self.ParseObject(G, partRel[1], seen, results)
                seen.append(partRel[1])

        # Construct deftemplates for definition relations
        for isRel in outIsRelations:
            if not isRel[1] in seen:
                self.ParseObject(G, isRel[1], seen, results)
                seen.append(isRel[1])
        return slots

    def ParseDeftemplate(self, G, node, relations, seen, results):
        """Parses deftemplate definition from node and its dependencies"""
        slotList = []
        gotObjects = []
        
        # Get leading Strings.has relations, these are definitions for sinple slots
        outHasRelations = relations[gc.OutgoingRelations][Strings.has]

        if len(outHasRelations) > 0:
            for outHasRel in outHasRelations:
                # Parse object. If it is simple slot it will be returned
                newObjects = self.ParseObject(G, outHasRel[1], seen, results)
                if isinstance(newObjects, list):
                    gotObjects += newObjects
                elif newObjects:
                    gotObjects.append(newObjects)

        # Transform slot list
        slotList = [obj for obj in gotObjects if isinstance(obj, BLNlpClipsSlotMap)]

        # Check for id slot and add one if there is no one
        hasIdSlot = len([slot for slot in slotList if slot.Name == gc.SlotIdSuffix]) > 0
        if not hasIdSlot:
            slotList.append({"Name": gc.SlotIdSuffix})

        # Process aggregations
        if len(relations[gc.OutgoingRelations][Strings.part]) > 0:
            slots = self.ParseAggregationSlot(G, node, relations, seen, results)
            slotList += slots

        # Proceed extras
        if Strings.ExtraFields in G.node[node]:
            for extra in G.node[node][Strings.ExtraFields]:
                slotList.append({"Name": extra})

        # Configure deftemplate mapping
        if not node in seen:
            newTemplate = BLNlpClipsDeftemplateMap()
            newTemplate.TemplateName = node
            for slot in slotList:
                newTemplate.AddSlot(slot)

            # Add object to output
            results.AddDeftemplate(newTemplate)
            seen.append(node)

    def ParseDeffact(self, G, node, relations, valRelations, seen, results):
        """Parses fact definition from node"""
        facts = BLNlpClipsDeffactsMap()
        
        # Get related deftemplates
        for isRel in relations[gc.OutgoingRelations][Strings.is_]:
            self.ParseObject(G, isRel[1], seen, results)
            fact = BLNlpClipsFactMap()
            fact.SlotValues[gc.SlotIdSuffix] = node
            template = results.GetDeftemplate(isRel[1])
            fact.Template = template

            # Get slot names
            tmplSlotNames = [slot.Name for slot in template.Slots]

            # Get value definition relations
            for valRel in valRelations[gc.OutgoingRelations]:
                if valRel[1] in tmplSlotNames:
                    fact.SlotValues[valRel[1]] = valRel[2][Strings.val]

            # Fill aggregation slots
            if len(relations[gc.OutgoingRelations][Strings.in_]) > 0:
                ruleCounter = 1
                for rel in relations[gc.OutgoingRelations][Strings.in_]:
                    inRelNodeRelations = self.GetInOutRelationsForList(G, rel[1], [Strings.is_, Strings.req])
                    outIsRelations = inRelNodeRelations[gc.OutgoingRelations][Strings.is_]
                    for isRel in outIsRelations:
                        fact.SlotValues[isRel[1] + gc.SlotIdSuffix] = isRel[0]
                    if gc.EnumerateRequirements in rel[2] and rel[2][gc.EnumerateRequirements]:
                        processName = self.__GetCurrentProcessName(G, node)
                        ruleCounter = self.__ParseEnumerationRule(G, node, relations, inRelNodeRelations, processName, ruleCounter, results)


            # Fill extra slots
            extraRelNames = [slot.Name for slot in template.Slots if not slot.Name in fact.SlotValues]
            extraRels = self.GetInOutRelationsForList(G, node, extraRelNames)
            if len(extraRels[gc.OutgoingRelations]) > 0:
                for extraRel in list(extraRels[gc.OutgoingRelations].keys()):
                    if len(extraRels[gc.OutgoingRelations][extraRel]) > 0:
                        fact.SlotValues[extraRel] = extraRels[gc.OutgoingRelations][extraRel][0][1]

            # Add fact to list
            facts.AddFact(fact)

        # Add list to result
        results.AddDeffact(facts)

    def GetInOutRelationsForList(self, G, node, relations=[]):
        """Gets the relations for node, having ids from 'relations' list"""
        res = {gc.InputRelations: {}, gc.OutgoingRelations : {}}
        if len(relations) > 0:
            outEdges = [edge for edge in G.out_edges([node], data = True) if Strings.rel in edge[2]]
            inEdges = [edge for edge in G.in_edges([node], data = True) if Strings.rel in edge[2]]
        
            for rel in relations:
                outRelations = [r for r in outEdges if (Strings.rel, rel) in list(r[2].items())]
                res[gc.OutgoingRelations][rel] = outRelations
                inRelations = [r for r in inEdges if (Strings.rel, rel) in list(r[2].items())]
                res[gc.InputRelations][rel] = inRelations
        return res

    def GetInOutRelationshipsForList(self, G, node, relations=[]):
        """Gets the relationships for node, having marks from 'relations' list"""
        res = {gc.InputRelations: {}, gc.OutgoingRelations : {}}
        if len(relations) > 0:
            outEdges = [edge for edge in G.out_edges([node], data = True) if not edge[2] in [{}, None] ]
            inEdges = [edge for edge in G.in_edges([node], data = True) if not edge[2] in [{}, None]]
        
            for rel in relations:
                outRelations = [r for r in outEdges if rel in r[2]]
                res[gc.OutgoingRelations][rel] = outRelations
                inRelations = [r for r in inEdges if rel in r[2]]
                res[gc.InputRelations][rel] = inRelations
        return res

    def GetValRelations(self, G, node):
        """Get value relations for node
           Value relation sets a value of a slot
        """
        res = {gc.InputRelations: [], gc.OutgoingRelations : []}
        outEdges = [edge for edge in G.out_edges([node], data = True) if Strings.val in edge[2]]
        inEdges = [edge for edge in G.in_edges([node], data = True) if Strings.val in edge[2]]
        res[gc.OutgoingRelations] = outEdges
        res[gc.InputRelations] = inEdges

        return res

    def ParseDefrule(self, G, node, seen, results):
        """Parses defrule construct"""
        rule = BLNlpClipsDefruleMapping()
        
        # Get input templates
        relations = self.GetInOutRelationsForList(G, node, [Strings.input, Strings.is_])
        for rel in relations[gc.OutgoingRelations][Strings.input]:
            templ = results.GetDeftemplate(rel[1])
            if templ == None:
                self.ParseObject(G, rel[1], seen, results)
                templ = results.GetDeftemplate(rel[1])
            rule.AddInputTemplate(templ)

        # Get output templates
        for rel in relations[gc.OutgoingRelations][Strings.is_]:
            templ = results.GetDeftemplate(rel[1])
            if templ == None:
                self.ParseObject(G, rel[1], seen, results)
                templ = results.GetDeftemplate(rel[1])
            rule.AddOutputTemplate(templ)
            
            # Construct outputing fact for each deftemplate
            fact = BLNlpClipsFactMap()
            fact.Template = templ
        
        # Get captures
        captures = self.__ParseCaptures(G, node, seen, results)

        # Group captures by templates
        groupedCaptures = {}
        for capture in captures:
            if not capture.Deftemplate.TemplateName in groupedCaptures:
                groupedCaptures[capture.Deftemplate.TemplateName] = []
            groupedCaptures[capture.Deftemplate.TemplateName].append(capture)

        # Order templates by parent links
        def comparer(cl1, cl2):
            for c in cl1:
                if c.Parent in cl2:
                    return 1
            for c in cl2:
                if c.Parent in cl1:
                    return -1
            return 0

        sortedCaptureGroups = sorted(groupedCaptures.values(), key=ngutils.cmp_to_key(comparer))

        # Create capture conditions
        for group in sortedCaptureGroups:
            captureCondition = BLNlpClipsRuleCaptureCondition()
            captureCondition.Captures = group
            captureCondition.Deftemplate = group[0].Deftemplate
            rule.AddCondition(captureCondition)

        # Get results creation
        resTemplates = []
        for rel in relations[gc.OutgoingRelations][Strings.is_]:
            templ = results.GetDeftemplate(rel[1])
            if templ != None:
                resTemplates.append(templ)
        bindId = {"id": 1}
        for templ in resTemplates:
            fact = BLNlpClipsFactMap()
            fact.Template = templ
            for slot in templ.Slots:
                if slot.Name in G.node[node]:
                    fact.SlotValues[slot.Name] = self.__ParseSlotValue(G.node[node][slot.Name], rule, bindId)
            fact.Assert = True
            rule.AddOutputFact(fact)
            
        rule.Name = str(uuid.uuid4())#node

        if Strings.attrResultingCondition in G.node[node]:
            cond = G.node[node][Strings.attrResultingCondition]
            if cond != "":
                rule.WholeOutputCondition = self.__ParseSimpleCondition(cond)

        results.AddDefrule(rule)

    #========================Captures parsing==============================

    def __ParseCaptures(self, G, node, seen, results):
        relationships = self.GetInOutRelationshipsForList(G, node, [Strings.capture, Strings.captureFrom, Strings.captures])
        captures = []
        idCounter = 1
        for rel in relationships[gc.OutgoingRelations][Strings.capture]:
            idCounter = self.__ParseSingleCapture(G, node, rel, rel[2][Strings.capture], rel[2], idCounter, captures, results)
        for rel in relationships[gc.OutgoingRelations][Strings.captures]:
            for (name, cfrom) in rel[2][Strings.captures].items():
                idCounter = self.__ParseSingleCapture(G, node, rel, name, cfrom,idCounter, captures, results)
        return captures

    def __ParseSingleCapture(self, G, node, rel, name, cfrom, idCounter, captures, results):
        if not Strings.captureFrom in cfrom:
            return idCounter
            
        # Get capturing sources
        source = cfrom[Strings.captureFrom]
        sources = [source]
        if gc.CaptureSourceDelimiter in source:
            sources = source.split(gc.CaptureSourceDelimiter)
        sources.append(rel[1])
        templates = []
        prevTemplate = None
        for i in range(len(sources) - 1):
            capture = BLNlpClipsRuleCapture()
            capture.CaptureType = gc.CaptureSingle
            extraCapture = None

            s = sources[i]
            templ = results.GetDeftemplate(s)
            if templ == None:
                # Not template but slot capturing 
                templ = prevTemplate
            else:
                # Define prevTemplate to keep connection
                prevTemplate = templ

            if templ == None:
                self.ParseObject(G, s, seen, results)
                templ = results.GetDeftemplate(s)
                if not templ == None:
                    prevTemplate = templ

            # Got a template in sequense
            capture.Deftemplate = templ

            # Next element in sequence should be slot name
            slotName = sources[i + 1]
                    
            # Slot can be either slot with information or connecting-id-slot
            slot = templ.GetSlot(slotName)
            if slot == None:
                slot = templ.GetIdSlot(slotName)
            capture.Slot = slot
                    
            # Capture name would be either final slot name or id for next fact    
            if i == len(sources) - 2:
                capture.CaptureName = name
            else:
                capture.CaptureName = gc.CaptureIdBody + str(idCounter)
                idCounter += 1

                # Need to define extra capture
                ecDeftemplate = results.GetDeftemplate(slot.IdOf)
                ecSlot = ecDeftemplate.GetSlot("Id")

                # Check whether capture already exists
                if len([x for x in captures if x.Slot == ecSlot]) == 0:
                    # Define capture if there is no yet
                    extraCapture = BLNlpClipsRuleCapture()
                    extraCapture.CaptureType = gc.CaptureSingle
                    extraCapture.CaptureName = capture.CaptureName
                    extraCapture.Parent = capture
                    extraCapture.Deftemplate = ecDeftemplate
                    extraCapture.Slot = ecSlot
                prevTemplate = ecDeftemplate
                    
            if len([x for x in captures if x.Slot == slot]) == 0:
                captures.append(capture)
            if extraCapture != None:
                captures.append(extraCapture)
        return idCounter

    #=======================Resolutions parsing==================================
    def __ResolveQuotting(self, value):
        res = value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\'", "\\\'")
        if res.startswith("\\\""):
            res = "\"" + res[2:]
        if res.endswith("\\\""):
            res = res[:-2] + "\""
        if " " in res and not res.startswith("\""):
            res = "\"" + res
        if " " in res and not res.endswith("\""):
            res = res + "\""
        return res

    def __ParseSlotValue(self, value, rule, bindId):
        if not isinstance(value, str):
            return value
        elif not "%?" in value:
            return self.__ResolveQuotting(value)
        else:
            if len(value.split(" ")) == 1:
                return value[1:]
            else:
                if value.startswith("\""):
                    # Needs string concatenation
                    pieces = []
                    iter = re.finditer(gc.ClipsVariablesInGraphDescription, value)
                    prevPos = 0
                    for i in iter:
                        pieces.append(value[prevPos:i.regs[0][0]])
                        pieces.append(value[i.regs[0][0]:i.regs[0][1]])
                        prevPos = i.regs[0][1]
                    if prevPos != len(value) - 1:
                        pieces.append(value[prevPos:])
                    res = ""
                    for i in range(len(pieces) - 1):
                        res += "(" + gc.StrCat + " "
                    for i in range(len(pieces)):
                        if not "%?" in pieces[i]:
                            if i != 0:
                                res += "\""
                            res += pieces[i]
                            if i != len(pieces) - 1:
                                res += "\""
                        else:
                            res += pieces[i][1:]
                        res += " "
                        if i != 0:
                            res += ") " 
                    return res
                else:
                    # Currently simple condition
                    condExpr = gc.SimpleCondition
                    fm = re.fullmatch(condExpr, value)
                    if fm != None:
                        bind = BLNlpClipsVarBind()
                        bind.CaptureName = gc.BindedVariablePref + str(bindId["id"])
                        bindId["id"] += 1
                        bind.Value = fm.groups()[2]

                        condBind = BLNlpClipsConditionalVarBind()
                        condBind.CaptureName = bind.CaptureName
                        condBind.Value = fm.groups()[1]
                        condBind.Condition = self.__ParseSimpleCondition(fm.groups()[0])
                        rule.AddResolutionBind(bind)
                        rule.AddResolutionBind(condBind)
                        return "?" + bind.CaptureName

                    return value

    def __CompareSignToClipsSymbol(self, sign):
        if sign == "==":
            return gc.Equal
        elif sign in ["!=", "<>"]:
            return gc.NotEqual
        else:
            return sign

    def __ParseSimpleCondition(self, cond):
        str = cond
        if cond.startswith("%"):
            str = cond[1:]
        condGroups = re.fullmatch(gc.SingleComparison, str).groups()
        return "(" + self.__CompareSignToClipsSymbol(condGroups[1]) + " " +  condGroups[0] + " " + condGroups[2] + ")"

    def GetGatheringFunctions(self, G, res):
        """Gets all gathering functions by gathering marks in graph"""
        for node in G:
            if Strings.attrGather in G.node[node] and G.node[node][Strings.attrGather]:
                gf = BLNlpClipsGatheringFunction()
                gf.DeftemplateName = node
                res.AddGatheringFunction(gf)

    #=========================Rule priorities============================
    def GetRulePriorities(self, G, results):
        """Goes through results, looks for rules and sets priority for each of them"""
        rules = results.Defrules
        proceededRules = []
        curRulesSet = []
        curSalience = 10000

        # Fill the list of input templates, would be unshanged through all processing
        inputTemplates = set()
        for rule in rules:
            for tmp in rule.InputTemplates:
                inputTemplates.add(tmp.TemplateName)

        # We have to proceed all rules
        while len(proceededRules) < len(rules):
            outputTemplates = set()

            # Tke outputing template names from not proceeded rules
            for rule in rules:
                if not rule in proceededRules:
                    for tmp in rule.OutputTemplates:
                        outputTemplates.add(tmp.TemplateName)

            # Valid input templates at current iteration are the ones which are not produced with existing rules
            validInputs = inputTemplates.difference(outputTemplates)

            # Get applicable rules from not proceeded
            curRuleSet = [rule for rule in rules if not rule in proceededRules and len(set([templ.TemplateName for templ in rule.InputTemplates]).difference(validInputs)) == 0]

            # Set the proper priority for selected rules
            for rule in curRuleSet:
                rule.Priority = curSalience

            # Update proceeded list
            proceededRules += curRuleSet

            # Decrease salience
            curSalience -= 1


    # ===================== Enumeration rule =============================
    def __ParseEnumerationRule(self, G, node, relations, inRelNodeRelations, processName, ruleCounter, results):
        """Parses a rule which produces a list of dependencies"""
        enumResult = results.GetDeftemplate(gc.TemplateEnumerationResult)
        # Get required items
        inputReqRelationNames = set([r[0] for r in inRelNodeRelations[gc.InputRelations][Strings.req]])

        # Get items which take part in a step
        nodeInputToolRels = set([r[0] for r in relations[gc.InputRelations][Strings.tool]])

        # Get intersection
        applyingObjects = inputReqRelationNames.intersection(nodeInputToolRels)

        # If any then produce a rule
        if len(applyingObjects) > 0:
            # Create and name the rule
            enumRule = BLNlpClipsDefruleMapping()
            enumRule.Name = "Enumerate" + "".join(node.replace("\"", "").split()) + str(ruleCounter)
            # Templates
            enumRule.AddOutputTemplate(results.GetDeftemplate(gc.TemplateResult))
            enumRule.AddOutputTemplate(enumResult)

            # Go through objects list
            for reqRel in applyingObjects:
                # Fill output fact
                outFact = BLNlpClipsFactMap()

                # It would be clips assertion
                outFact.Assert = True

                # This is a fact with result id
                outFact.Resulting = True

                # Process in which result lives
                outFact.ResultingProcess = processName

                # Name of object and what is it
                outFact.SlotValues["Name"] = reqRel
                outFact.SlotValues["Templates"] = [r[1] for r in self.GetInOutRelationsForList(G, reqRel, [Strings.is_])[gc.OutgoingRelations][Strings.is_]]
                outFact.ResultingProperties.RelatedTo = self.__GetRelatedToDef(node, relations)
                if outFact.ResultingProperties.RelatedTo != BLNlpEnumResultFactRelation.Nothing:
                    outFact.SlotValues["RelatedTo"] = node

                # Fact template
                outFact.Template = enumResult
                enumRule.AddOutputFact(outFact)
            results.AddDefrule(enumRule)
            ruleCounter += 1
        return ruleCounter

    def __GetRelatedToDef(self, node, relations):
        """"""
        if len([r for r in relations[gc.OutgoingRelations][Strings.is_] if r[1] == Strings.ndProcess]) > 0:
            return BLNlpEnumResultFactRelation.Process
        elif len([r for r in relations[gc.OutgoingRelations][Strings.is_] if r[1] == Strings.ndStep]) > 0:
            return BLNlpEnumResultFactRelation.ProcessStep
        elif len([r for r in relations[gc.OutgoingRelations][Strings.is_] if r[1] == "ProcessSubStep"]) > 0:
            return BLNlpEnumResultFactRelation.ProcessSubStep
        else:
            return BLNlpEnumResultFactRelation.Nothing

    def __GetCurrentProcessName(self, G, node):
        """
        Walks through node relations and finds the first occurrence of 'in' relation which is applied to process object
        Search is done using relation "requires" of objects "in" passed node with requirements enumaration flag
        """
        prName = ""
        
        # Get targets of "in relations"
        relsIn = self.GetInOutRelationsForList(G, node, [Strings.in_, Strings.tool])
        inHolders = [rel[1] for rel in relsIn[gc.OutgoingRelations][Strings.in_]]
        
        # Get targets of "requires" relations
        reqTargets = set()
        for rel in relsIn[gc.InputRelations][Strings.tool]:
            reqTargets = reqTargets.union(set([r[1] for r in self.GetInOutRelationsForList(G, rel[0], [Strings.req])[gc.OutgoingRelations][Strings.req]]))

        # Do a search through "in" links
        while len(inHolders) and len(prName) == 0:
            nestedRels = self.GetInOutRelationsForList(G, inHolders[0], [Strings.is_, Strings.in_])
            isNames = [rel[1] for rel in nestedRels[gc.OutgoingRelations][Strings.is_]]
            
            # Once Process is met, return
            if Strings.ndProcess in isNames and inHolders[0] in reqTargets:
                prName = inHolders[0]
            else:
                inHolders += [rel[1] for rel in nestedRels[gc.OutgoingRelations][Strings.in_]]
            del inHolders[0]

        return prName

