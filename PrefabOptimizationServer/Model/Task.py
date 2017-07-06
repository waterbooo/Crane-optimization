import networkx as nx
import requests

from CommonGraphUtils import CommonGraphUtils as GUtils
from Consts import *

class Task(object):
    """description of class"""

    def __init__(self, name, properties):
        """ string name of the task """
        self.name = name
        """ dictionary of properties of the task (string mapped to tuple of float and string unit)"""
        self.properties = properties

    # Graph constants
    __kTaskBaseNode = "Task"

    # JSON tags
    __kTagTools = "tools"
    __kTagParameters = "parameters"
    __kTagRates = "rates"
    __kTagToolToRate = "tooltorate"
    __kTagAfterTask = "after"
    __kTagRelatedToProcesses = "processes"
    __kTagName = "name"
    __kTagProperties = "properties"
    __kTagAttributes = "attributes"

    # Mapping rules
    # TODO: Make this dynamic
    __kLookForKey = "lookForKey"
    __kKeyValue = "keyValue"
    __kKBToolKey = "kbToolKey"
    __kMappingRules = [
        # Rule for "saw notch" and "router notch": look for key 'notch' in Fusion task 
        # If so, find the value in kb task names
        # If found look for "notch" (router or saw) among kb task tool names list
        [{"lookForKey": "notch", "keyValue": "notch", "kbToolKey": "tools"}],

        # Rule for "screw machine screw" 
        # Just look for "screw" among keys in Fusion task and for "screw" in kb task name
        [{"lookForKey": "screw", "keyValue": "screw"}]

        ]

    # Task attributes types
    __kAttrTypes = set([
        Strings.actor,
        Strings.cost,
        Strings.duration,
        Strings.place,
        Strings.quantity,
        Strings.range,
        Strings.target,
        Strings.time,
        Strings.uses])

    def SendTasksToAPIServer(project_id, tasks):
        """
        Sends tasks to https://api.integratedbuildingdesign.autodesk.com
        params:
            project_id - id of project in db
            tasks - jsonifiable list of tasks descriptions
        """
        url = "https://api.integratedbuildingdesign.autodesk.com/worktasks/" + project_id
        r = requests.post(url, json = { 'project_id': project_id, 'tasks': tasks })

    def GetTasksFromAPIServer(project_id):
        """
        Gets tasks from https://api.integratedbuildingdesign.autodesk.com
        params:
            project_id - id of project in db
        returns:
            jsonifiable list of tasks descriptions or None in case of error
        """
        url = "https://api.integratedbuildingdesign.autodesk.com/worktasks/" + project_id
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        return None

    def __IsProcess(G, node):
        """Checks whether node is finally the process"""
        return GUtils.IsInstanceOfRoot(G, node, Strings.ndProcess)

    def __IsRate(G, node):
        """Checks whether node is finally the rate"""
        return GUtils.IsInstanceOfRoot(G, node, Strings.ndRate)

    def __IsTool(G, node):
        """Checks whether node is finally the tool"""
        return GUtils.IsInstanceOfRoot(G, node, Strings.ndTool)

    def __IsTask(G, node):
        """Checks whether node is finally the task"""
        return GUtils.IsInstanceOfRoot(G, node, Strings.ndTask)

    def __CheckTaskIsFinal(G, taskNode):
        """
        Looks into task node dependencies.
        If there are relations to process, tool and target, that is final task
        """

        if not Task.__IsTask(G, taskNode):
            return False

        # Process relation
        processRel = False
        partNodes = GUtils.GetOutRelNodes(G, taskNode, Strings.part)
        for node in partNodes:
            if Task.__IsProcess(G, node):
                processRel = True
                break
        if not processRel:
            return False

        # Tools relation
        toolRel = False
        usesNodes = GUtils.GetOutRelNodes(G, taskNode, Strings.uses)
        for node in usesNodes:
            if Task.__IsTool(G, node):
                toolRel = True
                break
        if not toolRel:
            return False

        # Target relation
        targetNodes = GUtils.GetOutRelNodes(G, taskNode, Strings.target)

        return len(targetNodes) != 0

        
    def __GetEndTasksNames(G):
        """Gets the final task names from the list"""
        taskNames = [node for node in G if Task.__CheckTaskIsFinal(G, node)]
        return taskNames
        
    def ParseTasksFromGraph(G):
        """
        Takes a networkx graph obtained from Dynamo or some else place
        Parses info about set of tasks from it
        params:
            G - NLP produced graph
        returns: 
            list of tasks from graph
        remarks:
            return list might be empty
        """
        
        resTasks = []

        taskNames = Task.__GetEndTasksNames(G)
        for tn in taskNames:

            task = Task(tn, {})

            # Processes
            nodes = GUtils.GetOutRelNodes(G, tn, Strings.part)
            task.properties[Task.__kTagRelatedToProcesses] = []
            for node in nodes:
                if Task.__IsProcess(G, node):
                    task.properties[Task.__kTagRelatedToProcesses].append(node)

            # Parameters
            nodes = GUtils.GetOutRelNodes(G, tn, Strings.has)
            task.properties[Task.__kTagParameters] = []
            for node in nodes:
                if GUtils.IsInstanceOfRoot(G, node, "Parameter"):
                    types = GUtils.GetOutRelNodes(G, node, Strings.type)
                    task.properties[Task.__kTagParameters].append({"name": node, "types": types})

            # Attributes
            task.properties[Task.__kTagAttributes] = {}
            for attrKey in Task.__kAttrTypes:
                attrValues = GUtils.GetOutRelNodes(G, tn, attrKey)
                if len(attrValues) != 0:
                    task.properties[Task.__kTagAttributes][attrKey] = attrValues

            # Order
            nodes = GUtils.GetOutRelNodes(G, tn, Strings.after)
            task.properties[Task.__kTagAfterTask] = []
            for node in nodes:
                if Task.__IsTask(G, node):
                    task.properties[Task.__kTagAfterTask].append(node)

            # Tools
            nodes = GUtils.GetOutRelNodes(G, tn, Strings.uses)
            task.properties[Task.__kTagTools] = []
            for node in nodes:
                if Task.__IsTool(G, node):
                    task.properties[Task.__kTagTools].append(node)

            # Rates / ToolToRates
            nodes = GUtils.GetInRelNodes(G, tn, Strings.associated)
            task.properties[Task.__kTagRates] = []
            task.properties[Task.__kTagToolToRate] = {}

            for node in nodes:
                if Task.__IsRate(G, node):
                    task.properties[Task.__kTagRates].append(node)
                    connections = GUtils.GetOutRelNodes(G, node, Strings.associated)
                    for c in connections:
                        if c in task.properties[Task.__kTagTools]:
                            if not c in task.properties[Task.__kTagToolToRate]:
                                task.properties[Task.__kTagToolToRate][c] = []
                            task.properties[Task.__kTagToolToRate][c].append(node)

            # Append task to res
            resTasks.append(task)

        return resTasks

    def __CheckKBTaskKeyForMatch(kbTask, key, value):
        """
        Checks whether any of values under key in kbTask contains value
        """
        try:
            lowervalue = value.lower()
            if key in kbTask[Task.__kTagProperties]:
                if isinstance(kbTask[Task.__kTagProperties][key], list):
                    for item in kbTask[Task.__kTagProperties][key]:
                        if lowervalue in item.lower():
                            return True
                else:
                    if lowervalue in item.lower():
                        return True
            return False
        except:
            return False
        

    def MapFusionToKB(kbTasks, fusionTasks):
        """Map kb and fusion tasks to each other"""
        res = {}

        if not kbTasks or not "tasks" in kbTasks or not fusionTasks:
            return res

        # Order tasks obtained from KB using graph structure
        tasksOrder = nx.DiGraph()
        mapNumber = 1
        for task in kbTasks["tasks"]:
            tasksOrder.add_node(task[Task.__kTagName])
            tasksOrder.node[task[Task.__kTagName]] = {"task": task, "mapNumber": mapNumber}
            mapNumber += 1
        for task in kbTasks["tasks"]:
            if Task.__kTagAfterTask in task[Task.__kTagProperties] and len(task[Task.__kTagProperties][Task.__kTagAfterTask]) > 0:
                for t in task[Task.__kTagProperties][Task.__kTagAfterTask]:
                    tasksOrder.add_edge(t, task[Task.__kTagName])

        seen = []
        
        # Go over task groups in fusion array
        for fgroup in fusionTasks.items():
            # Tasks are under the non-empty array values 
            if isinstance(fgroup[1], list) and len(fgroup[1]) > 0:
                baseItem = fgroup[1][0]
                ruleGroups = []

                # Find rulegroups for fusion task group
                for g in Task.__kMappingRules:
                    applicableRules = 0
                    for rule in g:
                        if rule[Task.__kLookForKey] in baseItem:
                            applicableRules += 1
                    if len(g) == applicableRules:
                        ruleGroups.append(g)
                
                # Map tasks from fusion tasks group to tasks from kb
                for ruleGroup in ruleGroups:
                    nodes = [node for node in tasksOrder if len([rule for rule in ruleGroup if rule[Task.__kKeyValue].lower() in node.lower()])]
                    if nodes:
                        for item in fgroup[1]:
                            nodeSet = []
                            for node in nodes:
                                for rule in ruleGroup:
                                    if Task.__kKBToolKey in rule:
                                        if Task.__CheckKBTaskKeyForMatch(tasksOrder.node[node]["task"], rule[Task.__kKBToolKey], item[rule[Task.__kKeyValue]]):
                                            nodeSet.append(node)
                                    else:
                                        nodeSet.append(node)
                            for node in nodeSet:
                                if not node in res:
                                    res[node] = {"orderMark":0, "tasks":[]}
                                res[node]["tasks"].append(item)
        
        # Mark graph levels
        from Optimization.Order.ConstructionOrdering import ConstructionOrdering
        ConstructionOrdering.markLevels(tasksOrder)

        for item in res.items():
            item[1]["orderMark"] = tasksOrder.node[item[0]]["level"]

        return res

    def GroupOrderFusionTasks(mappedTasks):
        """Groups tasks by order marks"""
        res = {}
        return res
