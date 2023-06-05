import nodeitems_utils
from .node_tree import NetworkTree
from .nodes import *


class ATNodeCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type == NetworkTree.bl_idname and
                context.space_data.edit_tree is not None and
                context.space_data.edit_tree.network_tree_type == "ANIMATION_TREE")


class SMNodeCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type == NetworkTree.bl_idname and
                context.space_data.edit_tree is not None and
                context.space_data.edit_tree.network_tree_type == "STATE_MACHINE")


node_categories = [
    ATNodeCategory("AT_INPUT", "Input", items=[
        nodeitems_utils.NodeItem(ATNodeTail.bl_idname),
        nodeitems_utils.NodeItem(ATNodeFrame.bl_idname),
        nodeitems_utils.NodeItem(ATNodeIk.bl_idname),
        nodeitems_utils.NodeItem(ATNodeClip.bl_idname),
        nodeitems_utils.NodeItem(ATNodeProxy.bl_idname),
        nodeitems_utils.NodeItem(ATNodeIdentity.bl_idname),
        nodeitems_utils.NodeItem(ATNodePose.bl_idname),
        nodeitems_utils.NodeItem(ATNodeInvalid.bl_idname),
        nodeitems_utils.NodeItem(ATNodeSubNetwork.bl_idname),
    ]),
    ATNodeCategory("AT_OUTPUT", "Output", items=[
        nodeitems_utils.NodeItem(ATNodeOutputAnimation.bl_idname),
    ]),
    ATNodeCategory("AT_COMBINE", "Combine", items=[
        nodeitems_utils.NodeItem(ATNodeBlend.bl_idname),
        nodeitems_utils.NodeItem(ATNodeBlendN.bl_idname),
        nodeitems_utils.NodeItem(ATNodeAddSubtract.bl_idname),
        nodeitems_utils.NodeItem(ATNodeAddN.bl_idname),
        nodeitems_utils.NodeItem(ATNodeMerge.bl_idname),
        nodeitems_utils.NodeItem(ATNodeMergeN.bl_idname),
    ]),
    ATNodeCategory("AT_MODIFY", "Modify", items=[
        nodeitems_utils.NodeItem(ATNodeFilter.bl_idname),
        nodeitems_utils.NodeItem(ATNodeMirror.bl_idname),
        nodeitems_utils.NodeItem(ATNodeExtrapolate.bl_idname),
        nodeitems_utils.NodeItem(ATNodeExpression.bl_idname),
        nodeitems_utils.NodeItem(ATNodeCapture.bl_idname),
        nodeitems_utils.NodeItem(ATNodeJointLimit.bl_idname),
    ]),
    ATNodeCategory("AT_STATE_MACHINE", "State Machine", items=[
        nodeitems_utils.NodeItem(ATNodeStateMachine.bl_idname),
        nodeitems_utils.NodeItem(ATNodeInlinedStateMachine.bl_idname),
    ]),
    ATNodeCategory("AT_LAYOUT", "Layout", items=[
        nodeitems_utils.NodeItem('NodeFrame'),
        nodeitems_utils.NodeItem('NodeReroute'),
    ]),

    SMNodeCategory("SM_STATE_MACHINE", "State Machine", items=[
        nodeitems_utils.NodeItem(SMNodeStart.bl_idname),
        nodeitems_utils.NodeItem(SMNodeState.bl_idname),
        nodeitems_utils.NodeItem(SMNodeStateMachine.bl_idname),
    ]),
    SMNodeCategory("SM_LAYOUT", "Layout", items=[
        nodeitems_utils.NodeItem('NodeFrame'),
    ]),
]


def register():
    nodeitems_utils.register_node_categories("SOLLUMZ_NT_MOVE_NETWORK_Categories", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("SOLLUMZ_NT_MOVE_NETWORK_Categories")