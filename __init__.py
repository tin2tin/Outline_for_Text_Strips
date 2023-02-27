bl_info = {
    "name": "Add Outline",
    "author": "tintwotin",
    "version": (1, 0),
    "blender": (2, 83, 0),
    "location": "Text Strip > Style > Add Outline",
    "description": "Add outline to text strips",
    "warning": "",
    "doc_url": "",
    "category": "Sequencer",
}

import bpy


class SEQUENCER_OT_outline(bpy.types.Operator):
    """Add outlines to selected text strips"""
    bl_label = "Add Outline"
    bl_idname = "sequencer.outline"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene and context.scene.sequence_editor)

    def execute(self, context):

        scene = bpy.context.scene
        sequencer = bpy.ops.sequencer
        context = bpy.context.scene.sequence_editor
        strips = bpy.context.selected_editable_sequences
        strips = sorted(strips, key=lambda strip: strip.frame_final_start)
        org = scene.sequence_editor.active_strip

        for i in range(0, len(strips)):
            if strips[i].type == 'TEXT':
                source_strip = strips[i]
                
                # Deselect all strips.
                for seq in scene.sequence_editor.sequences_all:
                    seq.select = False

                # Dublicate foreground text.
                strips[i].select = True
                strips[i].use_box = False
                strips[i].use_shadow = False
                bpy.ops.sequencer.duplicate_move(
                    SEQUENCER_OT_duplicate={},
                    TRANSFORM_OT_seq_slide={"value": (0, 2)})
                top_strip = scene.sequence_editor.active_strip

                # Add Glow strip.
                new_strip = scene.sequence_editor.sequences.new_effect(
                    name="Outline",
                    channel=strips[i].channel + 1,
                    type='GLOW',
                    frame_start=10,
                    frame_end=35,
                    seq1=strips[i])

                outline_width = int(strips[i].font_size/40) # Dynamic outline width
                new_strip.blur_radius = outline_width 
                new_strip.color_multiply = 10 # Outline opacity
                new_strip.quality = 1
                new_strip.threshold = 0
                new_strip.use_only_boost = True
                new_strip.boost_factor = 1
                new_strip.blend_type = 'ALPHA_OVER'

                # Add Color Balance modifier and set to black.
                context.active_strip = new_strip
                sequencer.strip_modifier_add(type='COLOR_BALANCE')
                new_strip.modifiers["Color Balance"].color_balance.lift = (0,0,0)
                new_strip.modifiers["Color Balance"].color_balance.gamma = (0,0,0)
                new_strip.modifiers["Color Balance"].color_balance.gain = (0,0,0)
                
                # Create a new driver for the font size of the second text strip
                driver = top_strip.driver_add("font_size")

                # Set the driver type
                driver.driver.type = "AVERAGE"

                var = driver.driver.variables.new()
                var.name = 'font_size'
                var.type = 'SINGLE_PROP'

                var.targets[0].id_type  = "SCENE"
                var.targets[0].id = bpy.context.scene
                var.targets[0].data_path = "sequence_editor.sequences_all["+chr(34)+source_strip.name+chr(34)+"].font_size"

        # Deselect all strips.
        for seq in scene.sequence_editor.sequences_all:
            seq.select = False

        scene.sequence_editor.active_strip = org 
        scene.sequence_editor.active_strip.select = True 
                
        return {'FINISHED'}


def panel_append(self, context):
    self.layout.separator()
    self.layout.operator("sequencer.outline")


def register():
    bpy.utils.register_class(SEQUENCER_OT_outline)
    bpy.types.SEQUENCER_PT_effect_text_style.append(panel_append)


def unregister():
    bpy.utils.unregister_class(SEQUENCER_OT_outline)
    bpy.types.SEQUENCER_PT_effect_text_style.remove(panel_append)


if __name__ == "__main__":
    register()
