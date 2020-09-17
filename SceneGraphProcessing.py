import networkx
import re

scene_graph_file = "2377804_scene_graph.graphml"
existence_keyword = "exists"
relation_keyword = "relation"
attribute_keyword = "attribute"

''' Note for Goonmeet: The way Lexical Gaps are identified here might not be ideal - should "this item isn't in the node"
 be treated as a gap or just a "nope, not present"?  We may need to put our heads together on that one; I think it
 could be argued that it's fine as is, because technically asking a question about the existence of something which
 doesn't exist opens up a lexical gap, even if it's an acceptable one?  Same goes for the target gap, at least 
 in the existence query'''


# Nodes are items (eventually attributes also), edges are positioning relationships (or eventually hasAttribute)

# ASSUMPTIONS:
# Users enter queries correct conforming to the format.
# When the user asks about, say "jersey", it's reasonable to look at jersey, jersey_1, and jersey_2; thus, the "_X"
# will be ignored


# Potential Graph modifications to simplify things: Add a tag of some sort that identifies objects as objects and
# attributes as such.  i.e. name: pants, type: object; name: orange, type: attribute

# Check each node in the scene graph to see if it has edges connected to it.  If it has no edges connected to it, flag
# a context gap on that node.
def contextGapCheck(sceneGraph):
    # Making a list of all the nodes that have context gaps.  It's unused at this point, but it may be useful at some
    # point?
    contextGappedNodes = []

    # Maybe not the most efficient thing - proof of concept, optimization can come later
    # Iterate through all the nodes of the graph, check their in/out edges and see if there's any that just don't have
    # edges
    for currentNode in sceneGraph.nodes:
        # Grab all the edges coming in and out of the current node and see if there are none.
        nodeOutEdges = sceneGraph.out_edges(currentNode)
        nodeInEdges = sceneGraph.in_edges(currentNode)
        allNodeEdges = list(nodeOutEdges) + list(nodeInEdges)
        if allNodeEdges == []:
            # If no edges connected to the node, a context gap may be in order.
            print("WARNING: Potential context gap identified!  Node " + currentNode + " has no edges connected to it!")
            contextGappedNodes.append(currentNode)
    return contextGappedNodes


# Handles queries asking about the existence of some item: exists(object).  Currently just scans the graph and detects
# lexical gaps if the object is not found and target gaps if multiple copies of the object are found.
# No gap resolution yet, just getting detection out the door for now.
def existenceQuery(queryContents: str, sceneGraph):
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

# Pants to the right of bat
def relationQuery(queryContents: str, sceneGraph):
    # Set a flag if the relation is found, and a list to store all of the found relations
    relationFound = False
    relationsMatchingQuery = []
    # Break up the query into its respective parts
    queryElements = queryContents.split(',')
    queryRelation = queryElements[0]
    querySource = queryElements[1]
    queryTarget = queryElements[2].split(')')[0]
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
        print("WARNING: Potential Target Gap identified.  Multiple node-edges sets match the queried relation.  " +
              "The list of these relations is as follows: " + str(relationsMatchingQuery))


# Strip off the "_#" at the end of an object name
def stripOffUnderscoreNumber(textToStrip):
    # For each node, strip off the "_#" if present - see assumptions at top of file
    regexPattern = r'_\d+'
    strippedText = re.sub(regexPattern, '', textToStrip)
    return strippedText


def main():
    # Load in the scene graph
    sceneGraph = networkx.read_graphml(scene_graph_file)
    # Prior to any querying, check for context gaps on certain items
    # Returns a list of nodes which have context gaps.  Currently unused but maybe eventually useful?
    contextGappedNodes = contextGapCheck(sceneGraph)
    # Get user query.  Eventually need to add attribute handling when attributes are available.
    userQuery = input("Please enter a query in the format KEYWORD(arguments), with the following options: \n " +
          existence_keyword + "(object) \n" + relation_keyword + "(relationString,object1,object2) \n")
    # Break query up into relevant parts
    queryType = userQuery.split('(', 1)[0]
    queryContents = userQuery.split('(', 1)[1]
    # Handle the exists(object) case
    if queryType == existence_keyword:
        existenceQuery(queryContents, sceneGraph)
        pass
    # Handle the relation(object1,object2) case
    if queryType == relation_keyword:
        relationQuery(queryContents, sceneGraph)
        pass
    # Handle the attribute case - NOT PRESENT
    if queryType == attribute_keyword:
        # ATTRIBUTE CASE
        pass

    print(sceneGraph)


main()