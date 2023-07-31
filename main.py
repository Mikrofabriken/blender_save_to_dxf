import bpy
import bmesh
import ezdxf
import os
from bpy.app.handlers import persistent
import itertools

class SAVEASDXF_OT_save_face_as_dxf(bpy.types.Operator):
    bl_idname = 'saveasdxf.save_face_as_dxf'
    bl_label = 'Save as DXF'

    @persistent
    def set_filename(self):
        if bpy.data.is_saved:
            print("Absolute path: {}".format(os.path.dirname(bpy.data.filepath)))
            self.filename = "{}/save_as_dxf.dxf".format(os.path.dirname(bpy.data.filepath))
        else:
            self.ShowMessageBox("You need to save the file to a directory before saving to DXF")

    def ShowMessageBox(self, message = "", title = "Save to DXF", icon = 'INFO'):

        def draw(self, context):
            self.layout.label(text=message)

        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

    def execute(self, context):
        doc = ezdxf.new("R2000")
        msp = doc.modelspace()

        self.set_filename()

        drawn = 0
        skipped = 0

        Z = None

        if bpy.context.active_object:
            o = bpy.context.active_object
            if o.mode == 'EDIT' and o.type == "MESH":
                print("{} is a mesh".format(o.name))
                m = bmesh.from_edit_mesh(o.data) 
                edges = []
                for f in m.faces:
                    if f.select:
                        print("Selected face")
                        for e in f.edges:
                            points = []
                            point1 = e.verts[0]
                            point2 = e.verts[1]
                            if Z is None:
                                Z = point1.co[2]
                                print("Setting Z to export to {}".format(point1.co[2]))
                            if point1.co[2] == Z and point2.co[2] == Z:
                                points.append( (point1.co[0], point1.co[1]) )
                                points.append( (point2.co[0], point2.co[1]) )
                            else:
                                skipped += 1

                            if len(points) > 1:
                                edges.append(points)

                # Have edges in a list, but dupes may exist. Remove the dupes
                edges.sort()
                draw_edges = list(edges for edges,_ in itertools.groupby(edges))

                for edge in draw_edges:
                    drawn += 1
                    print("drawing line between {} and {}) ".format(edge[0], edge[1]))
                    msp.add_lwpolyline(edge)
        
        doc.saveas(self.filename)

        self.ShowMessageBox("Saved {} edges to {}, skipped {} due to difference in Z plane".format(drawn, self.filename, skipped))
        return {'FINISHED'}

class SAVEASDXF_OT_select_objects_as_dxf(bpy.types.Operator):
    bl_idname = 'saveasdxf.save_objects_as_dxf'
    bl_label = 'Save as DXF'

    @persistent
    def set_filename(self):
        if bpy.data.is_saved:
            print("Absolute path: {}".format(os.path.dirname(bpy.data.filepath)))
            self.filename = "{}/save_as_dxf.dxf".format(os.path.dirname(bpy.data.filepath))
        else:
            self.ShowMessageBox("You need to save the file to a directory before saving to DXF")

    def ShowMessageBox(self, message = "", title = "Save to DXF", icon = 'INFO'):

        def draw(self, context):
            self.layout.label(text=message)

        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
 
    def execute(self, context):
        doc = ezdxf.new("R2000")
        msp = doc.modelspace()

        self.set_filename()

        drawn = 0
        skipped = 0
        Z = None # will be set on first point

        if len(bpy.context.selected_objects) > 0:
            s = bpy.context.selected_objects
            for o in s:
                if o.type == "MESH":
                    bpy.context.view_layer.objects.active = o
                    bpy.ops.object.mode_set(mode="EDIT")
                    m = bmesh.from_edit_mesh(o.data) 
                    print("{} is a mesh".format(o.name))
                    
                    edges = []
                    for f in m.faces:
                        for e in f.edges:
                            points = []
                            point1 = e.verts[0]
                            point2 = e.verts[1]
                            if Z is None:
                                Z = point1.co[2]
                                print("Setting Z to export to {}".format(point1.co[2]))
                            if point1.co[2] == Z and point2.co[2] == Z:
                                points.append( (point1.co[0], point1.co[1]) )
                                points.append( (point2.co[0], point2.co[1]) )
                            else:
                                skipped += 1

                            if len(points) > 1:
                                edges.append(points)

                    # Have edges in a list, but dupes may exist. Remove the dupes
                    edges.sort()
                    draw_edges = list(edges for edges,_ in itertools.groupby(edges))

                    for edge in draw_edges:
                        drawn += 1
                        print("drawing line between {} and {}) ".format(edge[0], edge[1]))
                        msp.add_lwpolyline(edge)

                bpy.ops.object.mode_set(mode="OBJECT")
        
        doc.saveas(self.filename)
        self.ShowMessageBox("Saved {} edges to {}, skipped {} due to difference in Z plane".format(drawn, self.filename, skipped))

        return {'FINISHED'}

bpy.utils.register_class(SAVEASDXF_OT_save_face_as_dxf)
bpy.utils.register_class(SAVEASDXF_OT_select_objects_as_dxf)

def face_menu_item_draw_func(self, context):
    self.layout.separator()
    self.layout.operator('saveasdxf.save_face_as_dxf', icon='DISK_DRIVE')

def selected_menu_item_draw_func(self, context):
    self.layout.separator()
    self.layout.operator('saveasdxf.save_objects_as_dxf', icon='DISK_DRIVE')
    
bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(face_menu_item_draw_func)
bpy.types.VIEW3D_MT_object_context_menu.append(selected_menu_item_draw_func)
