import os, util

# Create obj file, given an rlg file
def create_obj( rlg, split_files_by_group = False ):

    # take the filename, but remove the ".rlg" part
    filename_root = os.path.basename( rlg.name ).split(".")[0]

    # create the file (single file mode)
    if( not split_files_by_group ):
        filename = filename_root
        obj = open( DIR_PATH_OUTPUT + filename + ".obj", "w" )

    groups = read_rlg( rlg )['meshes']  # TODO: rework everything. This function shouldn't call read_rlg. Instead, a model3d object should be passed to it as argument


    # iterate on all the rlg's groups (meshes) and save their data in obj format
    for group, group_data in enumerate( groups ):

        # create the file (multi-file mode)
        if( split_files_by_group ):
            filename = filename_root + "_" + str(group)
            obj = open( DIR_PATH_OUTPUT + filename + ".obj", "w" )


        # Write the number of group
        obj.write( "g group " + str( group ) + "\n" )


        # Write the vertices of this group. In the .obj format, each vertex is a "v" follwed by the XYZ coordinates
        for vertex in group_data['vertices']: 
            obj.write( "v " + str( vertex["position"][0] ) + " " + str( vertex["position"][1] ) + " " + str( vertex["position"][2] ) + "\n" )
        

        # Write the faces of this group 
        first_vertex_identifier_of_group = group_data['vertices'][0]['absolute_id']  # get the absolute ID of the first vertex of the group

        for face in group_data['faces']:

            obj.write( "f " )  # write "f", which identifies a face in a .obj file    

            for relative_index in face:  # write the IDs of the vertices that make up the face

                # unlike for .rlg, in a .obj file, the IDs of the vertices aren't relative to their group (they don't reset on each group), so we must convert to absolute index
                # that is unless we're splitting files by group. In that case we just use the relative_index
                # also in a .obj file the first vertex has an ID of 1 (instead of 0 like .rlg), so we must add 1
                if( split_files_by_group ):
                    obj.write( str( relative_index + 1 ) + " " )  # write relative index + 1
                else: 
                    obj.write( str( first_vertex_identifier_of_group + relative_index + 1 ) + " " )  # write absolute index + 1

            obj.write( "\n" )


        # save the file (multi-file mode)
        if( split_files_by_group ):
            print(filename + ".obj was successfully created in output folder")
            obj.close()


    # save the file (single file mode)
    if( not split_files_by_group ):
        print(filename + ".obj was successfully created in output folder")
        obj.close()




def get_vertices_from_obj(filename):
    print("filename: " +filename)
    obj = open( DIR_PATH_INPUT_COMMON_FORMATS + filename + ".obj", "r" )
    # find the file size
    obj.seek(0,2)
    file_size = obj.tell()
    # read the data
    obj.seek(0,0)
    data = obj.read( file_size )

    # read the vertices of the obj file and convert them to array
    array_of_vertices = []
    vertex = []
    num_str = ''
    ignore = False
    column = 0
    for i in data:
        # If first character of row is not v, ignore the whole row
        if(i != 'v' and column == 0):
            ignore = True
        # If second character of row is not whitespace, ignore the whole row
        if(i != ' ' and column == 1):
            ignore = True
        # If current character is a comment ignore until new line
        if(i == '#'):
            ignore = True
        # If current character is part of a number, store it
        if(i in ['0','1','2','3','4','5','6','7','8','9','-','.','e']):
            num_str += i
        #  Increment the column
        column += 1
        # At the end of a number, parse the number
        if( (i == " " and len(num_str) != 0) or i == "\n"):
            if(not ignore):
                num = float(num_str)
                vertex.append(num)
            num_str = ''
            # Check if it's newline
            if(i == "\n"):
                if(len(vertex) > 0):
                    array_of_vertices.append(vertex)
                vertex = []
                ignore = False
                column = 0
        
    obj.close()
    return array_of_vertices