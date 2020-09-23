import re
import networkx

# Handles queries asking about the existence of some item: exists(object).  Currently just scans the graph and detects
# lexical gaps if the object is not found and target gaps if multiple copies of the object are found.
# No gap resolution yet, just getting detection out the door for now.
def itemExistenceQuery(queryContents: str, sceneGraph):
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
    if objectFound == True and len(listOfMatchingNodes) == 1:
        print("SUCCESS! " + queriedObject + " exists in the graph!")


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


# Strip off the "_#" at the end of an object name
def stripOffUnderscoreNumber(textToStrip):
    # For each node, strip off the "_#" if present - see assumptions at top of file
    regexPattern = r'_\d+'
    strippedText = re.sub(regexPattern, '', textToStrip)
    return strippedText
