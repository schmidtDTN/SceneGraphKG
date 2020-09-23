import networkx
from QuestionHandling import *

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
        itemExistenceQuery(queryContents, sceneGraph)
        pass
    # Handle the relation(object1,object2) case
    if queryType == relation_keyword:
        relationQueryHandler(queryContents, sceneGraph)
        pass
    # Handle the attribute case - NOT PRESENT
    if queryType == attribute_keyword:
        # ATTRIBUTE CASE
        pass

    print(sceneGraph)


main()