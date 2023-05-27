import bpy
import nodeitems_utils
from .node_tree import NodeTree
from .nodes import *


class NodeCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == NodeTree.bl_idname


node_categories = [
    NodeCategory("INPUT", "Input", items=[
        nodeitems_utils.NodeItem(NodeClip.bl_idname),
        nodeitems_utils.NodeItem(NodeEmpty.bl_idname),
    ]),
    NodeCategory("OUTPUT", "Output", items=[
        nodeitems_utils.NodeItem(NodeOutputAnimation.bl_idname),
    ]),
    NodeCategory("COMBINE", "Combine", items=[
        nodeitems_utils.NodeItem(NodeBlend.bl_idname),
        nodeitems_utils.NodeItem(NodeBlendN.bl_idname),
        nodeitems_utils.NodeItem(NodeAddSubtract.bl_idname),
    ]),
    NodeCategory("MODIFY", "Modify", items=[
        nodeitems_utils.NodeItem(NodeFilter.bl_idname),
        nodeitems_utils.NodeItem(NodeExpression.bl_idname),
    ]),
]


def register():
    nodeitems_utils.register_node_categories("MoveNetworkNodeCategory", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("MoveNetworkNodeCategory")