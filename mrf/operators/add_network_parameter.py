import bpy
from ..nodes.node_tree import NetworkTree
from ...sollumz_helper import SOLLUMZ_OT_base
from ..execution.network_player import NetworkPlayer

class SOLLUMZ_OT_MOVE_NETWORK_add_network_parameter(SOLLUMZ_OT_base, bpy.types.Operator):
    bl_idname = "sollumz.move_network_add_network_parameter"
    bl_label = "Add MoVE Network Parameter"
    bl_action = bl_label

    parameter_name_prop: bpy.props.StringProperty()
    parameter_name: bpy.props.StringProperty()
    parameter_type: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == "NODE_EDITOR" and
                space.tree_type == NetworkTree.bl_idname and
                space.edit_tree is not None and
                space.edit_tree.bl_idname == NetworkTree.bl_idname)

    def run(self, context):
        node_tree = context.space_data.edit_tree
        network = node_tree.network_root or node_tree
        if self.parameter_name == "":
            return False

        if self.parameter_type == "float":
            network.network_parameters.try_add_float(self.parameter_name)
        elif self.parameter_type == "bool":
            network.network_parameters.try_add_bool(self.parameter_name)
        elif self.parameter_type == "clip":
            network.network_parameters.try_add_clip(self.parameter_name)
        elif self.parameter_type == "asset":
            network.network_parameters.try_add_asset(self.parameter_name)
        else:
            return False

        setattr(network, self.parameter_name_prop, "")  # clear the text field
        return True
