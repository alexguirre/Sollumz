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
        nodeitems_utils.NodeItem(NodeTail.bl_idname),
        nodeitems_utils.NodeItem(NodeFrame.bl_idname),
        nodeitems_utils.NodeItem(NodeIk.bl_idname),
        nodeitems_utils.NodeItem(NodeClip.bl_idname),
        nodeitems_utils.NodeItem(NodeProxy.bl_idname),
        nodeitems_utils.NodeItem(NodeIdentity.bl_idname),
        nodeitems_utils.NodeItem(NodePose.bl_idname),
        nodeitems_utils.NodeItem(NodeInvalid.bl_idname),
        nodeitems_utils.NodeItem(NodeSubNetwork.bl_idname),
    ]),
    NodeCategory("OUTPUT", "Output", items=[
        nodeitems_utils.NodeItem(NodeOutputAnimation.bl_idname),
    ]),
    NodeCategory("COMBINE", "Combine", items=[
        nodeitems_utils.NodeItem(NodeBlend.bl_idname),
        nodeitems_utils.NodeItem(NodeBlendN.bl_idname),
        nodeitems_utils.NodeItem(NodeAddSubtract.bl_idname),
        nodeitems_utils.NodeItem(NodeAddN.bl_idname),
        nodeitems_utils.NodeItem(NodeMerge.bl_idname),
        nodeitems_utils.NodeItem(NodeMergeN.bl_idname),
    ]),
    NodeCategory("MODIFY", "Modify", items=[
        nodeitems_utils.NodeItem(NodeFilter.bl_idname),
        nodeitems_utils.NodeItem(NodeMirror.bl_idname),
        nodeitems_utils.NodeItem(NodeExtrapolate.bl_idname),
        nodeitems_utils.NodeItem(NodeExpression.bl_idname),
        nodeitems_utils.NodeItem(NodeCapture.bl_idname),
        nodeitems_utils.NodeItem(NodeJointLimit.bl_idname),
    ]),
    NodeCategory("STATE_MACHINE", "State Machine", items=[
        nodeitems_utils.NodeItem(NodeStateMachine.bl_idname),
        nodeitems_utils.NodeItem(NodeInlinedStateMachine.bl_idname),
        nodeitems_utils.NodeItem(NodeState.bl_idname),
    ]),
    NodeCategory("LAYOUT", "Layout", items=[
        nodeitems_utils.NodeItem('NodeFrame'),
        nodeitems_utils.NodeItem('NodeReroute'),
    ]),
]


def register():
    nodeitems_utils.register_node_categories("MoveNetworkNodeCategory", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("MoveNetworkNodeCategory")