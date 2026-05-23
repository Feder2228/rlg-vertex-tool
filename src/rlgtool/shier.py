"""
shier module
functions for decoding/encoding shier files
"""
from . import nlgutil
from . import rlg_data_structures
from . import util


def get_parent_bone_hash(shierfile, bone_hash : int) -> int:
    """get the hash of the parent bone

    Args:
        shierfile: file .shier
        bone_hash: the hash of the bone
    Return:
        the hash of the parent bone
    """
    bone_index = bone_hash_to_bone_shier_index(shierfile, bone_hash)
    root_section = nlgutil.get_section_tree(shierfile)
    parent_info_section = root_section.get_children_by_type(b'\x80\x09')[0]
    shierfile.seek(parent_info_section.body_location() + bone_index*4, 0)
    bone_index = int.from_bytes(shierfile.read(4))
    return bone_shier_index_to_bone_hash(shierfile, bone_index)



def bone_hash_to_bone_shier_index(shierfile, bone_hash : int) -> int:
    """get the index used inside the shier file to reference bone

    Args:
        shierfile: file .shier
        bone_hash: the hash of the bone
    Return:
        the index associated to the bone hash
    """
    root_section = nlgutil.get_section_tree(shierfile)
    hash_section = root_section.get_children_of_type(b'\x80\x03')[0]
    shierfile.seek(hash_section.body_location(), 0)
    for i in range(hash_section.size):
        current_hash = int.from_bytes(shierfile.read(4))
        if current_hash == bone_hash:
            return i
    return None




def bone_shier_index_to_bone_hash(shierfile, bone_index : int) -> int:
    """get the bone hash

    Args:
        shierfile: file .shier
        bone_index: the index that identifies the bone inside of a shier file
    Return:
        the hash of the bone
    """
    root_section = nlgutil.get_section_tree(shierfile)
    hash_section = root_section.get_children_of_type(b'\x80\x03')[0]
    shierfile.seek(hash_section.body_location() + bone_index*4, 0)
    return int.from_bytes(shierfile.read(4))




def organize_bone_hierarchy(shierfile, root : rlg_data_structures.RlgModel):
    """organize the bones of a model as a tree

    Mutates model and the elements of its bones list.
    model.root_bone will be set to a fake bone, whose children will be the
    level 1 bones that were found

    Args:
        shierfile: file .shier
        model: RlgModel object
    """
    root_bone = rlg_data_structures.RlgBone(hash_id=-1, matrix=None)
    for bone in root.bones:
        parent_bone_hash = get_parent_bone_hash(shierfile=shierfile, bone_hash=bone.hash_id)
        parent = root.get_bone_by_id(hash_id=parent_bone_hash)
        if parent != None:
            parent.children.append(bone)
        else:
            root_bone.children.append(bone)
    root.root_bone = root_bone




def get_bone_float_vector(shierfile, bone_hash : int) -> tuple[float]:
    """get the float vec
    """
    bone_index = bone_hash_to_bone_shier_index(shierfile=shierfile, bone_hash=bone_hash)
    root_section = nlgutil.get_section_tree(shierfile)
    hash_section = root_section.get_children_of_type(b'\x80\x10')[0]
    shierfile.seek(hash_section.body_location() + bone_index*12, 0)
    return (util.bytes_to_float(shierfile.read(4)), util.bytes_to_float(shierfile.read(4)), util.bytes_to_float(shierfile.read(4)))