from . import dae
from . import rlg
from . import nlgutil
from .rlg_data_structures import *
import copy


# SECTION IDENTIFIER CONSTANTS
SECTION_RLG_ROOT = b'\xb0\x00'
SECTION_STADIUM_WRAPPER = b'\xb1\x00'
SECTION_BUN_ROOT = b'\x00\x01'


def export_rlg_as_dae(rlgpath, daepath=None, shierpath=None):
    """Export a 3d model and create a dae file

    Args:
        rlgpath: path of the rlg file
        daepath: path of the dae file to be created. If not specified it
            will automatically be set
        shierpath: path of the shier file (optional)
    """
    if daepath == None:
        daepath = rlgpath + '.dae' 

    # TODO: make a function for this
    rlgfile = open(rlgpath, 'rb')
    l1_sections = nlgutil.get_section_tree(file=rlgfile)
    if l1_sections[0].type == SECTION_RLG_ROOT:
        section = l1_sections[0]
    rlgroot = rlg.read_rlg(rlgfile=rlgfile, root_section=section, shierpath=shierpath)

    dae.create_dae(rlgroot=rlgroot, filepath=daepath, bone_tree_mode=(shierpath!=None))
    print('created dae file at {0}'.format(daepath))
    rlgfile.close()




def generate_rlg_from_rlg_and_dae(srcrlgpath, dstrlgpath, daepath):
    """patch an rlg file using the data found in the provided dae file

    Args:
        srcrlgpath: path of the source rlg file
        dstrlgpath: path of the new rlg file
        daepath: path of the dae file
    """

    new_rlgroot = dae.read_dae(daepath)

    # get the data of the original rlg file as a rlgroot object
    srcrlg = open(srcrlgpath, "rb")
    l1_sections = nlgutil.get_section_tree(file=srcrlg)
    if l1_sections[0].type == SECTION_RLG_ROOT:
        section = l1_sections[0]
    old_rlgroot = rlg.read_rlg(srcrlg, root_section=section)

    # create the destination file and open it
    dstrlg = open(dstrlgpath, "wb")

    rlg.patch_rlg(srcrlg=srcrlg, 
                  dstrlg=dstrlg, 
                  new_root=new_rlgroot, 
                  old_root=old_rlgroot,
                  root_section=section,
                  keep_old_indices=False)
    print('created rlg file at {0}'.format(dstrlgpath))
    srcrlg.close()
    dstrlg.close()




def triangle(source_rlg_path : str, destination_rlg_path : str):
    """Replace the vertices and faces of the provided rlg file and turn
    the 3D object into a triangles

    Args:
        rlgs: path of the source rlg file
        rlgd: path 
    """
    old_root = rlg.read_rlg(rlgpath=source_rlg_path)
    new_root = copy.deepcopy(old_root)

    for model in new_root.models:
        for mesh in model.meshes:
            mesh.vertices.clear()
            mesh.indices.clear()

    mesh0 = model.meshes[0]
    mesh0.vertices = [
        RlgVertex(position=[-0.5, 0, 0], normal=[0, -1.0, 0], uv0=[0.0, 0.0]),
        RlgVertex(position=[0.5, 0, 0], normal=[0, -1.0, 0], uv0=[0.0, 0.0]),
        RlgVertex(position=[0, 0, 1.0], normal=[0, -1.0, 0], uv0=[0.0, 0.0])
    ]
    mesh0.indices = [0,2,1]

    rlg.patch_rlg(srcpath=source_rlg_path, dstpath=destination_rlg_path,
                  new_root=new_root, keep_old_indices=False)
    print('rlg file created')




def weird_triangle_thing(source_rlg_path : str, destination_rlg_path : str):
    """Replace the vertices and faces of the provided rlg file and turn
    the 3D object into a weird shape

    Args:
        rlgs: path of the source rlg file
        rlgd: path 
    """
    old_root = rlg.read_rlg(rlgpath=source_rlg_path)
    new_root = copy.deepcopy(old_root)

    for model in new_root.models:
        for mesh in model.meshes:
            mesh.vertices.clear()
            mesh.indices.clear()

    mesh0 = model.meshes[0]
    mesh0.vertices = [
        RlgVertex(position=[-1.0, 0, 0], normal=[0, 1.0, 0], uv0=[0.0, 0.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[0.0, 0, 0], normal=[0, 1.0, 0], uv0=[0.0, 0.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[1.0, 0, 0], normal=[0, 1.0, 0], uv0=[0.0, 0.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[1.0, 0, 1.0], normal=[0, 1.0, 0], uv0=[0.0, 0.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[1.5, 0, 3.5], normal=[0, 1.0, 0], uv0=[0.0, 0.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[0.0, 0, 2.0], normal=[0, 1.0, 0], uv0=[0.0, 0.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[-1.0, 0, 2.0], normal=[0, 1.0, 0], uv0=[0.0, 0.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[-1.0, 0, 1.0], normal=[0, 1.0, 0], uv0=[0.0, 0.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
    ]
    mesh0.indices = [0,1,7,7,7,1,1,3,2,3,3,4,5,5,5,6,7]
    # mesh0.indices = [0,1,7,7,7,1,1,2,3,3,3,4,5,5,5,6,7]
    # START A FACE AT AN EVEN INDEX FOR IT TO HAVE ITS NORMAL POINT TOWARDS THE COUNTERCLOCKWISE SIDE
    # odd index for clockwise, I guess

    rlg.patch_rlg(srcpath=source_rlg_path, dstpath=destination_rlg_path,
                  new_root=new_root, keep_old_indices=False)
    print('rlg file created')




def cube(source_rlg_path : str, destination_rlg_path : str):
    """Replace the vertices and faces of the provided rlg file and turn
    the 3D object into a weird shape

    Args:
        rlgs: path of the source rlg file
        rlgd: path 
    """
    old_root = rlg.read_rlg(rlgpath=source_rlg_path)
    new_root = copy.deepcopy(old_root)

    for model in new_root.models:
        for mesh in model.meshes:
            mesh.vertices.clear()
            mesh.faces.clear()

    mesh0 = model.meshes[0]
    mesh0.vertices = [
        RlgVertex(position=[-0.5, -0.5, 0.0], normal=[-0.7, -0.7, -0.7], uv0=[0.0, 0.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[0.5, -0.5, 0.0], normal=[0.7, -0.7, -0.7], uv0=[1.0, 0.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[0.5, 0.5, 0.0], normal=[0.7, 0.7, -0.7], uv0=[0.0, 0.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[-0.5, 0.5, 0.0], normal=[-0.7, 0.7, -0.7], uv0=[1.0, 0.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[-0.5, -0.5, 1.0], normal=[-0.7, -0.7, 0.7], uv0=[0.0, 1.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[0.5, -0.5, 1.0], normal=[0.7, -0.7, 0.7], uv0=[1.0, 1.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[0.5, 0.5, 1.0], normal=[0.7, 0.7, 0.7], uv0=[0.0, 1.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
        RlgVertex(position=[-0.5, 0.5, 1.0], normal=[-0.7, 0.7, 0.7], uv0=[1.0, 1.0], bone_ids=[0,0,0,0], bone_weights=[1.0,0.0,0.0,0.0]),
    ]
    mesh0.decode_indices([0,1,5,5,5,0,
                     0,5,4,4,4,1,
                     1,2,6,6,6,1,
                     1,6,5,5,5,2,
                     2,3,7,7,7,2,
                     2,7,6,6,6,3,
                     3,0,4,4,4,3,
                     3,4,7,7,7,4,
                     4,5,6,6,6,4,
                     4,6,7,7,7,0,
                     0,2,1,1,1,0,
                     0,3,2
                     ])

    rlg.patch_rlg(srcpath=source_rlg_path, dstpath=destination_rlg_path,
                  new_root=new_root, keep_old_indices=False)
    print('rlg file created')

    """
    (new) mario.rlg
    00 00 00 01  00 05 00 05  00 05 00 00  00 00 00 05
    00 04 00 04  00 04 00 01  00 01 00 02  00 06 00 06
    00 06 00 01  00 01 00 06  00 05 00 05  00 05 00 02
    00 02 00 03  00 07 00 07  00 07 00 02  00 02 00 07
    00 06 00 06  00 06 00 03  00 03 00 00  00 04 00 04
    00 04 00 03  00 03 00 04  00 07 00 07  00 07 00 04
    00 04 00 05  00 06 00 06  00 06 00 04  00 04 00 06
    00 07 00 07  00 07 00 00  00 00 00 02  00 01 00 01
    00 01 00 00  00 00 00 03  00 02 00 02  00 02 00 00
    """

    """
    (old) cube_mario.rlg
    00 00 00 01  00 05 00 05  00 05 00 00  00 00 00 05
    00 04 00 04  00 04 00 01  00 01 00 02  00 06 00 06
    00 06 00 01  00 01 00 06  00 05 00 05  00 05 00 02
    00 02 00 03  00 07 00 07  00 07 00 02  00 02 00 07
    00 06 00 06  00 06 00 03  00 03 00 00  00 04 00 04
    00 04 00 03  00 03 00 04  00 07 00 07  00 07 00 04
    00 04 00 05  00 06 00 06  00 06 00 04  00 04 00 06
    00 07 00 07  00 07 00 00  00 00 00 02  00 01 00 01
    00 01 00 00  00 00 00 03  00 02 00 00
    """