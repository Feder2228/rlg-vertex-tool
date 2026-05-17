import re

TAB = "  "
XML_TAG = '<?xml version="1.0" encoding="utf-8"?>'

# REGEX FOR XML PARSING
REGEX_TAG = r'<[^>]*>'
REGEX_NAME_FOR_OPENING_OR_BODYLESS_TAG = r'(?<=<)[^\s>\/]+(?=[>\s\/])' 
REGEX_NAME_FOR_CLOSING_TAG = r'(?<=<)\/[^\s>\/]+(?=[>\s])'
REGEX_ATTRIBUTE_KEY = r'(?<=\s)[^\s=]+(?==)'
REGEX_ATTRIBUTE_VALUE = r'(?<==")[^"]+(?=")'
REGEX_IS_TAG_BODYLESS = r'\/[\s]*>'
REGEX_CONTENT = r'[^>]*(?=<\/)'
REGEX_COMMENT = r'<!--.*?-->'  # needs re.DOTALL
REGEX_IS_COMMENT = r'<!--'

class XmlNode:
    """Class representing an element of an XML file

    Attributes:
        name (str): The tag's name
        attributes (dict): Dict of the tag's attributes
        has_body (bool): True if has a body. False otherwise
        content: The text content of the element (not including children tags)
        children: (list): List of children nodes
    """
    def __init__(self, name : str, attributes={}, has_body=True, content=''):
        """Initialize XmlNode object

        Args:
            name (str): The tag's name
            attributes (dict): Dict of the tag's attributes
            has_body (bool): True if has a body. False otherwise
            content: The text content of the element (not including children tags)
        Returns:
            new XmlNode object
        """
        self.name = name
        self.attributes = attributes
        self.has_body = has_body
        self.content = content
        self.children = []
    

    def append_child(self, new_child):
        """Add child to self

        Args:
            new_child (XmlNode): element to add as child
        Returns:
            the added child
        """
        self.children.append( new_child )
        return new_child


    def get_string_xml(self) -> str:
        """Convert XmlNode to a string

        Returns:
            A string that is formatted like the contents of an xml file
            containing the tag self and its children.
        """
        return self._get_string_xml_rec(0)
    

    def _get_string_xml_rec(self, level : int) -> str:
        """Auxiliary method for get_string_xml

        Args:
            level: how many levels to indent by
        Returns:
            A string that is formatted like the contents of an xml file
            containing the tag self and its children. Indented by (level)
            tabulations
        """
        xml = ''

        # write the tag name
        xml += (TAB * level) + '<' + self.name 

        # write all the attributes
        for key in self.attributes:
            xml += ' {0}="{1}"'.format(key, self.attributes[key]) 

        # close the angular bracket
        if self.has_body:
            xml += '>' 
        else:
            xml += ' />\n' 
            return xml

        # write content
        xml += self.content 

        # go newline if there are children
        if len(self.children) > 0:
            xml += '\n' 

        # children tags
        for child in self.children:
            xml += child._get_string_xml_rec(level+1)

        # close tag
        if len(self.children) > 0:
            xml += (TAB * level)
        xml += '</{0}>\n'.format(self.name) 

        return xml


    def get_string_tree_of_names(self) -> str:
        """Convert XmlNode to a string

        Returns:
            A string containing just the names of tag self and its children.
        """
        return self._get_string_tree_of_names_rec(0)


    def _get_string_tree_of_names_rec(self, level : int) -> str:
        """Auxiliary method for get_string_xml

        Args:
            level: how many levels to indent by
        Returns:
            A string containing just the names tag self and its children.
        """
        children_tree_of_names = ""
        for child in self.children:
            children_tree_of_names += child._get_string_tree_of_names_rec(level+1)
        return (" "*level) + self.name + "\n" + children_tree_of_names
    

    def get(self, key : str) -> str:
        """Get the value of an attribute from self 

        Args:
            key: key of the attribute 
        Returns:
            self.attributes[key] if it exists
        """
        if not key in self.attributes:
            return None
        return self.attributes[key]
    

    def find(self, name : str, attributes = {}):
        """Find a child of self that has the specified attributes

        For a node to be a match it must have a matching name and for each
        specified attribute key, the value must correspond.

        For example, the search: name="input", attributes={ 'semantic' : 'VERTEX' }
        matches the tag: <input semantic="VERTEX" source="#model-vertex" offset="0" />
        but doesn't match: <input semantic="NORMAL" source="#model-vertex" offset="0" /> because semantic is not 'VERTEX'

        Args:
            name: name of the tag to look for
            attributes: a dict containing the attributes that the target node must have
        Returns:
            The first occurrence of a matching XmlNode
        """
        found = self.findall(name, attributes)
        if len(found) > 0:
            return found[0]
        return None
    
    # find nodes that have matching information.
    def findall(self, name : str|None, attributes = {}): 
        """Find children of self that have the specified attributes

        Return a list containing all the matching nodes.
        For a node to be a match it must have a matching name and for each
        specified attribute key, the value must correspond.

        For example, the search: name="input", attributes={ 'semantic' : 'VERTEX' }
        matches the tag: <input semantic="VERTEX" source="#model-vertex" offset="0" />
        but doesn't match: <input semantic="NORMAL" source="#model-vertex" offset="0" /> because semantic is not 'VERTEX'

        Args:
            name: name of the tag to look for
            attributes: a dict containing the attributes that the target node must have
        Returns:
            A list containing all matching XmlNode objects. Empty list if none is found
        """
        is_match = True
        list_of_matches = []

        # if this tag doesn't have the specified name, no match
        # if no name is specified, skip this check
        if name != None and self.name != name:
            is_match = False

        for key in attributes:
            # if this node doesn't have this attribute key, no match
            if key not in self.attributes:
                is_match = False
            # if this node has the this attribute key, but it's not associated to the same value, no match
            elif attributes[key] != self.attributes[key]:
                is_match = False

        # if this node is a match, add it to the match list
        if is_match:
            list_of_matches.append(self)
        
        # look recursively for matches in child nodes
        for child in self.children:
            matching_nodes = child.findall(name, attributes)
            if len(matching_nodes) > 0:
                list_of_matches.extend(matching_nodes)
        return list_of_matches
    

    def findid(self, id : str):
        """A shortcut to find the child that has the corresponding id 
        attribute value
        """
        return self.find(None, { 'id': id })
    


# create an xml file given the file path and an XmlNode object
def create_xml(filepath : str, xmlnode):
    """Generate an xml file from XmlNode object

    Args:
        filepath: path of the file to be created
        xmlnode: root node of the xml file to be created
    """
    xmlfile = open(filepath, 'w')
    xmlfile.write(XML_TAG + '\n')
    xmlfile.write(xmlnode.get_string_xml())
 



def read_xml(filepath : str) -> XmlNode:
    """Read XML file

    Get a tree of nodes from an XML file

    Args:
        filepath: path of the file to be read
    Returns:
        self.attributes[key] if it exists
    """
    xmlfile = open(filepath, "r")

    file_str = xmlfile.read()
    pos = 0

    # list that keeps track of opened tags.
    # each element is a Xml_node object
    tag_stack = []  
    root_node = None

    while True:
        # get the next xml tag
        tag = parse_first_xml_tag(file_str[pos:])
        if tag == None:
            return root_node

        pos += tag['length'] + tag['offset']  # update position (move to the end of the tag that was just found) TODO: optimize

        if(tag['is_closing_tag']):
            tag_stack.pop()  
        else:
            xml_node = XmlNode(tag['name'], tag['attributes'], tag['has_body'], tag['content'])
            # if the stack isn't empty, this tag is a child of the node at the top of the stack
            if len(tag_stack) > 0:
                tag_stack[-1].append_child(xml_node) 
            # if the stack is empty, this node has no parents, so it's the root node (unless it doesn't have a body, in that case it's just the ?xml tag)
            elif tag['has_body']:
                root_node = xml_node
            # put the current node in the stack if it has a body. We'll need it for the next iteration
            if tag['has_body']:
                tag_stack.append(xml_node)
    



def parse_first_xml_tag(text): 
    """What the fuck. TODO maybe rework this?

    read the string and find the first xml tag
    return: a dict containing:
    tag name
    a dict of attributes
    a bool that is true if it's a closing tag </like_this>
    a bool, false if it's a tag that has no body <like_this/> it needs to have the slash at the end!
    an integer, length of the tag.
    an integer, offset of the tag from the beginning of the string. The place where the tag starts in the string

    Args:
        text: content of the xml file?
    Returns: 
        dict. Kms.
    """
    tag = ''
    while True:
        tag_match = re.search(REGEX_TAG, text)  # tag_match: string containing just the tag, delimited by <>
        if tag_match == None:
            return None

        tag = tag_match.group()
        tag_offset = tag_match.span()[0]  # position of the tag into the string

        # If it's not a comment, break from this loop and parse the tag values
        is_comment_match = re.search(REGEX_IS_COMMENT, tag)
        if is_comment_match == None:
            break

        # If it is a comment, ignore it and look for the next tag
        #
        # From the "text" string remove the comment, so that on next iteration
        # the text starts from after the comment, and the comment isn't detected
        # again, which otherwise would cause an infinite loop.
        #
        comment_match = re.search(REGEX_COMMENT, text, re.DOTALL)
        if(comment_match == None):  
            return None  # if the comment doesn't match, this is probably the end of the file
        end_of_comment = comment_match.span()[1]
        text = text[ end_of_comment: ] 

    # detect tag name and detect whether it's a closing or opening tag
    tag_name = ""
    is_closing_tag = False
    opening_tag_name_match = re.search(REGEX_NAME_FOR_OPENING_OR_BODYLESS_TAG, tag)
    if(opening_tag_name_match != None):
        tag_name = opening_tag_name_match.group()
    else:
        closing_tag_name_match = re.search( REGEX_NAME_FOR_CLOSING_TAG, tag )
        if(closing_tag_name_match != None):
            tag_name = closing_tag_name_match.group()
            is_closing_tag = True

    # get tag attributes
    attributes = get_xml_tag_attributes(tag)

    # determine if it's a tag that has no body (like this: <img/> )
    has_body = False
    if tag_name == '?xml':
        has_body = False
    else:
        bodyless_match = re.search(REGEX_IS_TAG_BODYLESS, tag)
        if bodyless_match == None:
            has_body = True  # if the regex doesn't match, this means it's NOT a tag that ends in "/>" or such, so it has a body

    # get the content of the tag
    content = ""
    if has_body and not is_closing_tag:
        # example: "<tag> content <child_tag>"  becomes: "tag> content "
        text_before_angular_open_bracket = text.split("<")[1]  
        # example: "tag> content"  becomes: " content "
        text_outside_angular_brackets = text_before_angular_open_bracket.split(">")[1]  
        content = text_outside_angular_brackets.replace("\n", "")  # strip all newline characters

    returned_dict = {
        'name' : tag_name,
        'attributes' : attributes,
        'content' : content,
        'is_closing_tag' : is_closing_tag,
        'has_body' : has_body,
        'length' : len( tag ),
        'offset' : tag_offset
    }
    return returned_dict




def get_xml_tag_attributes(text : str) -> dict:
    """Parse an xml tag and read its attributes

    Args:
        text: string representing an xml tag
    Returns: 
        dict of attributes
    """
    pos = 0
    attributes = {}

    while True:
        matches = match_first_attribute_of_xml_tag(text[pos:])
        # if the attributes are over, break out of the loop
        if matches == None:
            break
        attributes.update({ matches[0].group() : matches[1].group() })
        pos += matches[1].span()[1] + 1 # find the end of the tag value. Start parsing next one from there

    return attributes




def match_first_attribute_of_xml_tag(text : str) -> list:
    """Return match objects for the attribute key and attribute value

    Args:
        text: string representing an xml tag, or part of it
    Returns: 
        list of two match objects. One the attribute key and one for the attribute value
    """
    attribute_key_match = re.search(REGEX_ATTRIBUTE_KEY, text)
    attribute_value_match = re.search(REGEX_ATTRIBUTE_VALUE, text)
    if(attribute_key_match == None):
        return None
    return [attribute_key_match, attribute_value_match]


