This is a prototype of a scene graph question-answering system which can detect (and eventually resolve) knowledge gaps.

Right now, it takes in a GraphML scene graph (currently not passed in but rather set in a global variable in the file) and handles user queries regarding existence of certain objects or relations between certain objects.

Also, it checks for context gaps on graph load and returns a list of the nodes which have no edges connected to them.  The list is currently unused but may be useful at some point in the future.

The format for the possible queries which can be entered are as follow:
    exists(objectName) - queries the existence of an object, equivalent to asking "is there a objectName?"  Format for asking about the existence of a bat would be: exists(bat)
    relation(relationString,object1Name,object2Name) - queries whether the two objects in question are connected by an edge with a label that EXACTLY matches the relation string.  i.e. if you want to ask "is a player to the left of a hat?", the format would be:
    relation(to the left of,player,hat)

Good examples of phrases that will currently trigger lexical and target gaps for each relation are below:

exists(cat) - Lexical Gap

exists(bat) - Target Gap

relation(to the left of,pants,bat) - Lexical Gap

relation(to the right of,pants,bat) - Target Gap


09-23-2020: Added non-yes/no queries about relations.  
relation(?,o1,o2) - Return a list of all edges with o1 as source and o2 as target.
relation(r1,?,o2) - Return a list of all sources with a relation r1 and target o2.
relation(r1,o1,?) - Return a list of all targets with a relation r1 and source o2.

Example phrases that will provide results:

relation(?,pants,bat) - returns an answer

relation(?,spectator,bat) - returns nothing

relation(to the right of,spectator,?) - returns an answer

relation(to the left of,spectator,?) - returns nothing

relation(to the left of,?,spectator) - returns an answer

relation(to the right of,?,spectator) - returns nothing


09-23-2020: Added attribute existence querying
Examples:

attribute(pink,shorts) - Returns that the object "shorts" has the attribute "pink"

attribute(black,shorts) - Returns that the object "shorts" does not have the attribute "black"

attribute(big,shorts) - Returns a Lexical Gap because "big" does not exist in the graph

09-23-2020: Added non-yes/no queries for attributes
Examples:

attribute(?,shorts) - Returns that "shorts" has the attribute "pink"

attribute(?,cap) - Raises a Target Gap because there are two caps that have different attributes; POTENTIALLY INTERESTING FOR VQA?

attribute(?,lady) - Returns that "lady" has no attributes.

attribute(red,?) - Returns that "wall" and "shirt" are associated with the attribute "red"

attribute(big,?) - Returns a Lexical Gap because "big" does not exist in the graph.

09-23-2020: Now able to ask multiple queries without rerunning the system; just enter "q", "exit", or "quit" to end the run.