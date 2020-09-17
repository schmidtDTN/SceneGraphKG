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