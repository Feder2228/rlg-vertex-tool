import re

# REGEX FOR XML PARSING
REGEX_TAG = r'<[^>]*>'
REGEX_NAME_FOR_OPENING_OR_BODYLESS_TAG = r'(?<=<)[^\s>\/]+(?=[>\s\/])' 
REGEX_NAME_FOR_CLOSING_TAG = r'(?<=<)\/[^\s>\/]+(?=[>\s])'
REGEX_ATTRIBUTE_KEY = r'(?<=\s)[^\s=]+(?==)'
REGEX_ATTRIBUTE_VALUE = r'(?<==")[^"]+(?=")'
REGEX_IS_TAG_BODYLESS = r'\/[\s]*>'
REGEX_CONTENT = r'[^>]*(?=<\/)'

class Xml_node:
    def __init__( self, name, attributes, has_body, content ):
        self.name = name
        self.attributes = attributes
        self.has_body = has_body
        self.content = content
        self.children = []
    
    def append_child( self, new_child ):
        self.children.append( new_child )

    # returns a string containing a tree of tag names
    def get_string_tree_of_names( self ):
        return self.get_string_tree_of_names_rec( 0 )

    def get_string_tree_of_names_rec( self, level ):
        children_tree_of_names = ""
        for child in self.children:
            children_tree_of_names += child.get_string_tree_of_names_rec( level+1 )
        return (" "*level) + self.name + "\n" + children_tree_of_names
    
    # find the first node that has matching information
    def find_node( self, name, attributes = {} ):
        return self.find_all_nodes( name, attributes )[0]
    
    # find nodes that have matching information.
    def find_all_nodes( self, name, attributes = {} ): 

        is_match = True

        list_of_matches = []

        # if this tag doesn't have the specified name, no match
        # if no name is specified, skip this check
        if name != None and self.name != name:
            is_match = False

        # iterate on all the attributes that were passed to this function
        # for this Xml_node object to be a match, it must have all those attribute keys, and they all need to have the same values
        # it doesn't have to only have those keys. It can have other keys too    
        #
        # for example, the search: name="input", attributes={ 'semantic' : 'VERTEX' }
        # matches the tag: <input semantic="VERTEX" source="#model-vertex" offset="0" />
        # but doesn't match: <input semantic="NORMAL" source="#model-vertex" offset="0" /> because semantic is not 'VERTEX'
        #
        for key in attributes:

            # if this node doesn't have this attribute key, no match
            if key not in self.attributes:
                is_match = False

            # if this node has the this attribute key, but it's not associated to the same value, no match
            elif attributes[key] != self.attributes[key]:
                is_match = False

        # if this node is a match, add it to the match list
        if is_match:
            list_of_matches.append( self )
        
        # look recursively for matches in child nodes
        for child in self.children:
            matching_nodes = child.find_all_nodes( name, attributes )
            if len( matching_nodes ) > 0:
                list_of_matches.extend( matching_nodes )

        return list_of_matches
    


# get a tree of nodes from an xml file
def get_xml_tree( dae ):
    # list that keeps track of opened tags.
    # each element is a Xml_node object
    tag_stack = []  

    file_str = dae.read()
    pos = 0

    root_node = None


    while True:

        # get the next xml tag
        tag = parse_first_xml_tag( file_str[pos:] )

        # when there are no more xml tags, return root_node
        if tag == None:
            return root_node

        pos += tag['length'] + tag['offset']  # update position (move to the end of the tag that was just found)


        # if you found a closing tag, remove last tag from the stack
        if( tag['is_closing_tag'] ):
            tag_stack.pop()  

        # if you found an opening tag...
        else:
            # make an Xml_node out of it
            xml_node = Xml_node( tag['name'], tag['attributes'], tag['has_body'], tag['content'] )

            # if the stack isn't empty, this tag is a child of the node at the top of the stack
            if len( tag_stack ) > 0:
                tag_stack[-1].append_child( xml_node ) 
            
            # if the stack is empty, this node has no parents, so it's the root node (unless it doesn't have a body, in that case it's just the ?xml tag)
            elif tag['has_body']:
                root_node = xml_node

            # put the current node in the stack if it has a body. We'll need it for the next iteration
            if tag['has_body']:
                tag_stack.append( xml_node )

            # for node in tag_stack:
            #     print( "DEBUG: stack " + str( node.name ) )
            # print( "DEBUG: stack_size " + str( len(tag_stack) ) ) 
    
    


# read the string and find the first xml tag
# return: a dict containing:
# tag name
# a dict of attributes
# a bool that is true if it's a closing tag </like_this>
# a bool, false if it's a tag that has no body <like_this/> it needs to have the slash at the end!
# an integer, length of the tag.
# an integer, offset of the tag from the beginning of the string. The place where the tag starts in the string
def parse_first_xml_tag( text ): 

    tag_match = re.search( REGEX_TAG, text )  # tag_match: string containing just the tag, delimited by <>

    if tag_match == None:
        return None

    tag = tag_match.group()
    tag_offset = tag_match.span()[0]  # position of the tag into the string


    # detect tag name and detect whether it's a closing or opening tag
    tag_name = ""
    is_closing_tag = False

    opening_tag_name_match = re.search( REGEX_NAME_FOR_OPENING_OR_BODYLESS_TAG, tag )

    if( opening_tag_name_match != None ):

        tag_name = opening_tag_name_match.group()

    else:
        closing_tag_name_match = re.search( REGEX_NAME_FOR_CLOSING_TAG, tag )

        if( closing_tag_name_match != None ):

            tag_name = closing_tag_name_match.group()
            is_closing_tag = True



    # get tag attributes
    attributes = get_xml_tag_attributes( tag )


    # detect if it's a tag that has no body (like this: <img/> )
    has_body = False

    if tag_name == '?xml':

        has_body = False

    else:

        bodyless_match = re.search( REGEX_IS_TAG_BODYLESS, tag )

        if bodyless_match == None:

            has_body = True  # if the regex doesn't match, this means it's NOT a tag that ends in "/>" or such, so it has a body


    # get the content of the tag
    content = ""
    if has_body and not is_closing_tag:
        # example: "<tag> content <child_tag>"  becomes: "tag> content "
        text_before_angular_open_bracket = text.split("<")[1]  
        # example: "tag> content"  becomes: " content "
        text_outside_angular_brackets = text_before_angular_open_bracket.split(">")[1]  
        content = text_outside_angular_brackets.replace( "\n", "" )  # strip all newline characters

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




def get_xml_tag_attributes( text ):

    pos = 0

    attributes = {}

    while True:

        matches = match_first_attribute_of_xml_tag( text[pos:] )

        # if the attributes are over, break out of the loop
        if matches == None:
            break

        attributes.update( { matches[0].group() : matches[1].group() } )

        pos += matches[1].span()[1] + 1 # find the end of the tag value. Start parsing next one from there

    return attributes




# return match objects for the attribute key and attribute value
def match_first_attribute_of_xml_tag( text ):

    attribute_key_match = re.search( REGEX_ATTRIBUTE_KEY, text )

    attribute_value_match = re.search( REGEX_ATTRIBUTE_VALUE, text )

    if( attribute_key_match == None ):
        return None

    return [ attribute_key_match, attribute_value_match ]