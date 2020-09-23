import re
import networkx

CONST_TYPE_LABEL = 'type'
CONST_ATTR_LABEL = 'attr'
CONST_HAS_ATTRIBUTE_EDGE = 'has_attribute'

# Handles queries asking about the existence of some item: exists(object).  Currently just scans the graph and detects
# lexical gaps if the object is not found and target gaps if multiple copies of the object are found.
# No gap resolution yet, just getting detection out the door for now.
def itemExistenceQuery(queryContents: str, sceneGraph, outputResults = True):
    # Set a flag for if the object queried was found in the node
    objectFound = False
    listOfMatchingNodes = []
    # Get the target of the query
    queriedObject = queryContents.split(')')[0]
    # Again, not particularly efficient but hey.
    for currentNode in sceneGraph:
        # For each node, strip off the "_#" if present - see assumptions at top of file
        nodeObjectName = stripOffUnderscoreNumber(currentNode)
        # If the name of the object matches the target of the query, flag as such and set the flag to true
        if nodeObjectName == queriedObject:
            print("Queried object found: " + currentNode)
            objectFound = True
            # Also append the node to the list of matching nodes for target gap detection
            listOfMatchingNodes.append(currentNode)
    # If nothing matching found, raise a lexical gap
    if objectFound == False:
        print("WARNING: Lexical Gap identified - the object queried " + queriedObject +
              " does not appear in the graph.")
    # If multiple nodes found that match the queried term, raise a target gap
    if len(listOfMatchingNodes) > 1:
        print("WARNING: Potential Target Gap identified.  Multiple nodes match the queried object.  The list of these "
              "objects is as follows: " + str(listOfMatchingNodes))
    if objectFound == True and len(listOfMatchingNodes) == 1 and outputResults == True:
        print("SUCCESS! " + queriedObject + " exists in the graph!")

    # Return objectFound for attribute check
    return objectFound


# Parse out relation query and see if it's about the existence of a relation or if it's a query about what items
# have a relation applied to them/what objects are on a relation with some object.
def relationQueryHandler(queryContents: str, sceneGraph):
    # Split out the query contents
    queryElements = queryContents.split(',')
    queryRelation = queryElements[0]
    querySource = queryElements[1]
    queryTarget = queryElements[2].split(')')[0]

    # If no question marks at any point in the query, it's a relation existence query.
    if queryRelation != '?' and querySource != '?' and queryTarget != '?':
        relationExistenceQuery(queryRelation, querySource, queryTarget, sceneGraph)
    # If there are question marks in one of the query slots, then the user is asking for a report on what items/
    # relations are associated with the provided items/relation
    else:
        # For now only allowing one unknown in the query.  Could expand this out to two question marks down the line
        # TODO
        if queryRelation == '?':
            findRelationOfItems(querySource, queryTarget, sceneGraph)
        elif querySource == '?':
            findSourceOfRelation(queryRelation, queryTarget, sceneGraph)
        elif queryTarget == '?':
            findTargetOfRelation(queryRelation, querySource, sceneGraph)


# If the query is in the format relation(?,o1,o2) - search through the graph for edges connecting o1 and o2.
def findRelationOfItems(querySource: str, queryTarget: str, sceneGraph):
    relationsMatchingQuery = []
    # Iterate through the scene graph to find the source node
    for currentNode in sceneGraph:
        # For each node, strip off the "_#" if present - see assumptions at top of file
        nodeObjectName = stripOffUnderscoreNumber(currentNode)
        # If the name of the object matches the source object in the query, see if the desired relationship is found
        if nodeObjectName == querySource:
            # Get the successors of the source node (successor = a node that receives a directed edge from the source)
            nodeSuccessors = sceneGraph.successors(currentNode)
            # Go through all of the successors found and check if any of them match the requested target
            for successor in nodeSuccessors:
                strippedSuccessor = stripOffUnderscoreNumber(successor)
                # If the successor matches the target, add the relation between them to the list of relations matching
                # the query
                if strippedSuccessor == queryTarget:
                    relationsMatchingQuery.append((currentNode,
                                                   sceneGraph.get_edge_data(currentNode, successor)['label'],
                                                   successor))
    if len(relationsMatchingQuery) == 0:
        print("WARNING: There is no relation found in the graph between " + querySource + " and "
              + queryTarget + ".")
    # If multiple nodes found that match the queried term, raise a target gap
    #if len(relationsMatchingQuery) > 1:
    #    print("WARNING: Potential Target Gap identified.  Multiple node-edges sets match the queried relation.\n" +
    #          "The list of these relations is as follows: " + str(relationsMatchingQuery))
    else:
        print("SUCCESS: Relation(s) found between the requested nodes!  The list is as follow: "
              + str(relationsMatchingQuery))


# If the query is in the format relation(r1,?,o2) - search the graph for a list of source nodes which have an edge
# r1 going to a target node o2.
def findSourceOfRelation(queryRelation: str, queryTarget: str, sceneGraph):
    queryMatches = []
    # Iterate through the scene graph to find the source node
    for currentNode in sceneGraph:
        # For each node, strip off the "_#" if present - see assumptions at top of file
        nodeObjectName = stripOffUnderscoreNumber(currentNode)
        # If the name of the object matches the target object in the query, see if the desired relationship is found
        if nodeObjectName == queryTarget:
            # Get the edges going in to the target node
            nodeInEdges = sceneGraph.in_edges(currentNode, data="label")
            # Go through all of the edges found and get the edge and target nodes as well as the source
            for source, target, edgeLabel in nodeInEdges:
                # If the edge matches the queried relation, add the triple to the list of matches
                if edgeLabel == queryRelation:
                    queryMatches.append((source, edgeLabel, currentNode))

    if len(queryMatches) == 0:
        print("WARNING: There is no source node found in the graph which has an edge of " + queryRelation +
              " and a target of " + queryTarget + ".")
    # If multiple nodes found that match the queried term, raise a target gap
    #if len(relationsMatchingQuery) > 1:
    #    print("WARNING: Potential Target Gap identified.  Multiple node-edges sets match the queried relation.\n" +
    #          "The list of these relations is as follows: " + str(relationsMatchingQuery))
    else:
        print("SUCCESS: Source(s) found with the requested relation and target!  The list is as follow: "
              + str(queryMatches))


# If the query is in the format relation(r1,o1,?) - search the graph for a list of target nodes which have an edge
# r1 coming from a source node o1.
def findTargetOfRelation(queryRelation: str, querySource: str, sceneGraph):
    queryMatches = []
    # Iterate through the scene graph to find the target node
    for currentNode in sceneGraph:
        # For each node, strip off the "_#" if present - see assumptions at top of file
        nodeObjectName = stripOffUnderscoreNumber(currentNode)
        # If the name of the object matches the source object in the query, see if the desired relationship is found
        if nodeObjectName == querySource:
            # Get the edges going out of the source node
            nodeOutEdges = sceneGraph.out_edges(currentNode, data="label")
            # Go through all of the edges found and get the edge and source nodes as well as the target
            for source, target, edgeLabel in nodeOutEdges:
                # If the edge matches the queried relation, add the triple to the list of matches
                if edgeLabel == queryRelation:
                    queryMatches.append((currentNode, edgeLabel, target))

    if len(queryMatches) == 0:
        print("WARNING: There is no target node found in the graph which has an edge of " + queryRelation +
              " and a source of " + querySource + ".")
    # If multiple nodes found that match the queried term, raise a target gap
    # if len(relationsMatchingQuery) > 1:
    #    print("WARNING: Potential Target Gap identified.  Multiple node-edges sets match the queried relation.\n" +
    #          "The list of these relations is as follows: " + str(relationsMatchingQuery))
    else:
        print("SUCCESS: Target(s) found with the requested relation and source!  The list is as follow: "
              + str(queryMatches))


# Take in a query about a relation (ex: relation(to the left of,pants,bat)) and return whether or not that relation
# exists in the graph
def relationExistenceQuery(queryRelation: str, querySource: str, queryTarget: str, sceneGraph):
    # Set a flag if the relation is found, and a list to store all of the found relations
    relationFound = False
    relationsMatchingQuery = []
    # Iterate through the scene graph to find the source node
    for currentNode in sceneGraph:
        # For each node, strip off the "_#" if present - see assumptions at top of file
        nodeObjectName = stripOffUnderscoreNumber(currentNode)
        # If the name of the object matches the source object in the query, see if the desired relationship is found
        if nodeObjectName == querySource:
            # Get the edges going out of the source node
            nodeOutEdges = sceneGraph.out_edges(currentNode, data="label")
            # Go through all of the edges found and get the source and target nodes as well as the edge label
            for source, target, edgeLabel in nodeOutEdges:
                strippedTarget = stripOffUnderscoreNumber(target)
                # the source equivalence should always be true because of the prior check
                if strippedTarget == queryTarget and edgeLabel == queryRelation:
                    relationFound = True
                    relationsMatchingQuery.append((source, edgeLabel, target))
                    print(source + " " + edgeLabel + " " + target)
    # If nothing matching found, raise a lexical gap
    if relationFound == False:
        print("WARNING: Lexical Gap identified - the relation queried " + querySource + " " + queryRelation + " "
              + queryTarget + " does not appear in the graph.")
    # If multiple nodes found that match the queried term, raise a target gap
    if len(relationsMatchingQuery) > 1:
        print("WARNING: Potential Target Gap identified.  Multiple node-edges sets match the queried relation.\n" +
              "The list of these relations is as follows: " + str(relationsMatchingQuery))


# Parse out the query and route to the appropriate function
def attributeQueryHandler(queryContents: str, sceneGraph):
    queryElements = queryContents.split(',')
    queryAttribute = queryElements[0]
    queryObject = queryElements[1].split(')')[0]

    # If there are no question marks in the query, we just check flatly if the queried object has the queried attribute.
    if queryAttribute != '?' and queryObject != '?':
        # Before checking for attribute, check for existence of the object.
        objectExists = itemExistenceQuery(queryElements[1], sceneGraph, False)
        attributeExists = itemExistenceQuery(queryElements[0] + '_attr)', sceneGraph, False)
        if objectExists == True and attributeExists == True:
            attributeCheckQuery(queryAttribute, queryObject, sceneGraph)
    elif queryAttribute == '?':
        # Before checking for attribute, check for existence of the object.
        objectExists = itemExistenceQuery(queryElements[1], sceneGraph, False)
        if objectExists == True:
            listAttributesOfObject(queryObject, sceneGraph)
    elif queryObject == '?':
        # Before checking for attribute, check for existence of the object.
        attributeExists = itemExistenceQuery(queryElements[0] + '_attr)', sceneGraph, False)
        if attributeExists == True:
            listObjectsWithAttribute(queryAttribute, sceneGraph)

# Check if given attribute is applied to the given object.
# This could probably be incredibly improved, if tree is gross
# TODO: Could do something interesting with checking if the requested attribute exists in the graph at all or not
def attributeCheckQuery(queryAttribute: str, queryObject: str, sceneGraph):
    objectsWithAttribute = []

    # If the object does exist then move on
    for currentNode in sceneGraph:
        # For each node, strip off the "_#" if present - see assumptions at top of file
        nodeObjectName = stripOffUnderscoreNumber(currentNode)
        # If the name of the object matches the target of the query, flag as such and set the flag to true
        if nodeObjectName == queryObject:
            # Check if the node has the requested attribute attached
            for potentialAttribute in sceneGraph.neighbors(currentNode):
                # If the type of the neighbor is "attr" then it's an attribute
                if sceneGraph.nodes[potentialAttribute][CONST_TYPE_LABEL] == CONST_ATTR_LABEL:
                    # if the value of the node is the same as the queried attribute, then the queried object has the
                    # queried attribute
                    attributeName = stripOffUnderscoreAttr(potentialAttribute)
                    if attributeName == queryAttribute:
                        # Append the node to the list of matching nodes for target gap detection
                        objectsWithAttribute.append(currentNode)
    # If nothing matching found, inform user that the given attribute is not applied to the object
    if len(objectsWithAttribute) == 0:
        print("The object " + queryObject + " does not have the attribute " + queryAttribute + " in the scene graph.")
    # If multiple nodes found that match the queried term, raise a target gap
    elif len(objectsWithAttribute) > 1:
        print("WARNING: Potential Target Gap identified.  Multiple objects named " + queryObject + " have the queried "
                    "attribute " + queryAttribute + ". The list of these objects is as follows: " +
              str(objectsWithAttribute))
    elif len(objectsWithAttribute) == 1:
        print("SUCCESS! " + queryObject + " exists in the graph and has attribute " + queryAttribute + "!")


# Get list of objects which have a given attribute
def listAttributesOfObject(queryObject: str, sceneGraph):
    queryMatches = []
    objectCount = 0
    # Iterate through the scene graph to find the object node
    for currentNode in sceneGraph:
        # For each node, strip off the "_#" if present - see assumptions at top of file
        nodeObjectName = stripOffUnderscoreNumber(currentNode)
        # If the name of the object matches the object in the query, get its list of attributes
        if nodeObjectName == queryObject:
            # Count how many objects matching the queried object are found.
            objectCount = objectCount + 1
            # Get the edges going out of the object node
            nodeOutEdges = sceneGraph.out_edges(currentNode, data="label")
            # Go through all of the edges found and get the object, edge, and target of the edge
            for objectNode, attribute, edgeLabel in nodeOutEdges:
                # If the edge is the attribute edge, add the triple to the list of matches
                if edgeLabel == CONST_HAS_ATTRIBUTE_EDGE:
                    queryMatches.append((currentNode, CONST_HAS_ATTRIBUTE_EDGE, attribute))

    if len(queryMatches) == 0:
        print("WARNING: There is no attribute found in the graph that is attached to the object  " + queryObject + ".")
    # If multiple nodes found that match the queried term, raise a target gap
    # if len(relationsMatchingQuery) > 1:
    #    print("WARNING: Potential Target Gap identified.  Multiple node-edges sets match the queried relation.\n" +
    #          "The list of these relations is as follows: " + str(relationsMatchingQuery))
    else:
        if objectCount == 1:
            print("SUCCESS: The following attributes were found associated with the queried object!  The list is: "
                  + str(queryMatches))
        elif objectCount > 1:
            print("WARNING: Potential Target Gap identified.  Multiple objects match the queried object.\n" +
                  "The list of these objects and their attributes is as follows: " + str(queryMatches))


#Get list of attributes applied to given object.
def listObjectsWithAttribute(queryAttribute: str, sceneGraph):
    queryMatches = []
    attributeCount = 0
    # Iterate through the scene graph to find the queried attribute node
    for currentNode in sceneGraph:
        # For each node, strip off the "_attr" if present - see assumptions at top of file
        nodeAttributeName = stripOffUnderscoreAttr(currentNode)
        # If the name of the node matches the attribute in the query, see if the desired relationship is found
        if nodeAttributeName == queryAttribute:
            attributeCount = attributeCount + 1
            # Get the edges going in to the attribute node
            nodeInEdges = sceneGraph.in_edges(currentNode, data="label")
            # Go through all of the edges found and get the edge and target nodes as well as the source
            for objectNode, attribute, edgeLabel in nodeInEdges:
                # If the edge matches the queried relation, add the triple to the list of matches
                if edgeLabel == CONST_HAS_ATTRIBUTE_EDGE:
                    queryMatches.append((objectNode, CONST_HAS_ATTRIBUTE_EDGE, currentNode))
    if len(queryMatches) == 0:
        print("WARNING: There is no object found in the graph that is attached to the attribute "
              + queryAttribute + ".")
    # If multiple nodes found that match the queried term, raise a target gap
    # if len(relationsMatchingQuery) > 1:
    #    print("WARNING: Potential Target Gap identified.  Multiple node-edges sets match the queried relation.\n" +
    #          "The list of these relations is as follows: " + str(relationsMatchingQuery))
    else:
        if attributeCount == 1:
            print("SUCCESS: The following objects were found associated with the queried attribute!  The list is: "
                  + str(queryMatches))
        elif attributeCount > 1:
            print("WARNING: Potential Target Gap identified.  Multiple attributes match the queried attribute.\n" +
                  "The list of these attributes and the objects they affect is as follows: " + str(queryMatches))


# Strip off the "_#" at the end of an object name
def stripOffUnderscoreNumber(textToStrip):
    # For each node, strip off the "_#" if present - see assumptions at top of file
    regexPattern = r'_\d+'
    strippedText = re.sub(regexPattern, '', textToStrip)
    return strippedText


# Strip off the "_attr" at the end of an attribute name
def stripOffUnderscoreAttr(textToStrip):
    # For each node, strip off the "_attr" if present - see assumptions at top of file
    regexPattern = r'_attr$'
    strippedText = re.sub(regexPattern, '', textToStrip)
    return strippedText
