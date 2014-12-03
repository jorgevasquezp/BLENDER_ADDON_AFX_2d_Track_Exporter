bl_info = {
    "name": "After Effects Track Exporter",
    "author": "Jorge Vasquez",
    "version": (1, 0),
    "blender": (2, 65, 0),
    "location": "Clip Editor > Tools",
    "description": "Export track, and plane track information to Adobe After Effects",
    "warning": "",
    "wiki_url": "",
    "category": "Tracking"}

import bpy

class AFX_Track_Exporter:
    strings = {
		"main" : "Adobe After Effects 6.0 Keyframe Data",
		"units" : "Units Per Second",
		"width" : "Source Width",
		"height" : "Source Height",
		"source_aspect" : "Source Pixel Aspect Ratio",
		"comp_aspect" : "Comp Pixel Aspect Ratio",
		"position" : "Position",
		"position_units" : "Frame\tX pixels\tY pixels\tZ pixels",
		"rotation" : "Rotation",
		"rotation_units" : "Frame\tDegrees",
		"scale" : "Scale",
		"scale_units" : "Frame\tX percent\tY percent\tZ percent",
		"end" : "End of Keyframe Data",
		"corner_pin" : "Effects\tCorner Pin #1",
		"corner_pin_units" : "Frame\tX pixels\tY pixels",
		"corner_names" : ["Lower Left","Lower Right","Upper Right","Upper Left"],
		"header_types" : ["main","pos","rot","sca","c_pin","p_pin","end"]
		}
        
    def getFilePath(self):
        file_path = bpy.data.filepath
        file_name = bpy.path.basename(file_path)
        name_start = file_path.find(file_name)
        path = file_path[0:name_start]
        return path
        
    def write_afx_keyframe_header(self, data, type_index):
        #print("WRITE_AFX_KEYFRAME_HEADER Data: ",data)
        t = AFXtx.strings["header_types"][type_index]
        clip = bpy.context.space_data.clip
        scene = bpy.context.scene
        fps = scene.render.fps
        source_aspect  = clip.display_aspect[0]/clip.display_aspect[1]
        comp_aspect = scene.render.pixel_aspect_x/scene.render.pixel_aspect_y
        
        if t == "main":
            header = AFXtx.strings["main"]+"\n\n\t"+AFXtx.strings["units"]+"\t"+str(fps)+"\n"
            header = header + "\t"+AFXtx.strings["width"]+"\t"+str(clip.size[0])+"\n"
            header = header + "\t"+AFXtx.strings["height"]+"\t"+str(clip.size[1])+"\n"
            header = header + "\t"+AFXtx.strings["source_aspect"]+"\t"+str(source_aspect)+"\n"
            header = header + "\t"+AFXtx.strings["comp_aspect"]+"\t"+str(comp_aspect)+"\n\n"  
        elif t == "pos":
            header = AFXtx.strings["position"]+"\n\t"+AFXtx.strings["position_units"]+"\n"
        elif t == "rot":
            header = AFXtx.strings["rotation"]+"\n\t"+AFXtx.strings["rotation_units"]+"\n"
        elif t == "sca":
            header = AFXtx.strings["scale"]+"\n\t"+AFXtx.strings["scale_units"]+"\n"
        elif t == "end":
            header = "\n"+AFXtx.strings["end"]
        
        #print("HEADER: ", data)
        data = str(data) + header
        
        return data          
        
        #file.write(header)

    def write_afx_cp_keyframe_header(self, data, type_index, corner):
        #print("WRITE_AFX_CP_KEYFRAME_HEADER Data: ",data)
        
        t = AFXtx.strings["header_types"][type_index]
        if t == "c_pin":
            header = AFXtx.strings["corner_pin"]+"\t"+corner+"\n\t"+AFXtx.strings["corner_pin_units"]+"\n"	
        
        data = data + header
        
        return data
        
        #file.write(header)
            
    def calc_pos_from_corners(self, corners):
        sumX = 0.0
        sumY = 0.0
        for i in range(4):
            sumX += corners[i][0]
            sumY += corners[i][1]
        x = sumX/4        
        y = 1-(sumY/4) ## Y down
        return [x,y]

    def write_afx_pos_keyframe_header(self, data):
        #print("WRITE_AFX_POS_KEYFRAME_HEADER Data: ",data)
        pass
        
    def writeRawMarkers(self, data):
        #print("WRITERAWMARKERS Data: ",data)
        for frame in plane_track.markers:
           #print(dir(frame))       
           for current_corner in range(4): ## the corners are stored ina float4 0 = Lower Left, 1 = Lower Right, 2 = Upper Right, 3 = Upper Left)
              for current_component in range(2): ## the location of the corner are stored in a float2 x,y
                 
                 current_point = frame.corners[current_corner][current_component]

              data = data + " "
           data = data + "\n"
           
        return data
        
    def write_pos_data(self, data):
        #print("WRITE_POS Data: ",data)
        for marker in range(len(plane_track.markers)):
            n_format = "{0:.3f}"
            size = clip.size
            frame = plane_track.markers[marker].frame
            pos = calc_pos_from_corners(plane_track.markers[marker].corners)
            x = str(n_format.format(pos[0]*clip.size[0])) 
            y = str(n_format.format(pos[1]*clip.size[1]))
            z = "0" 
            line = "\t"+str(frame)+"\t"+x+"\t"+y+"\t"+"0"+"\n"
            
            data = data + line
        data = data + "\n"
        
        return data

    def write_cp_data(self, data, plane_track):
        
        clip = bpy.context.space_data.clip
        n_format = "{0:.3f}"
        for corner in range(4):

            data = AFXtx.write_afx_cp_keyframe_header(data,4,AFXtx.strings["corner_names"][corner])

            for marker in range(len(plane_track.markers)):
                frame = plane_track.markers[marker].frame
                x = str(n_format.format(plane_track.markers[marker].corners[corner][0]*clip.size[0]))
                y = str(n_format.format((1-plane_track.markers[marker].corners[corner][1])*clip.size[1]))
                line = "\t"+str(frame)+"\t"+x+"\t"+y+"\n"
                
                data = data +line
        data = data + "\n"
        
        return data
        
    def write_pos_from_single_track(self, data,track):
        #print("WRITE_POS_FROM_SINGLE_TRACK Data: ",data)
        for marker in range(len(track.markers)):
            n_format = "{0:.3f}"
            clip = bpy.context.space_data.clip
            size = clip.size
            frame = track.markers[marker].frame
            pos = track.markers[marker].co
            x = str(n_format.format(pos[0]*clip.size[0])) 
            y = str(n_format.format((1-pos[1])*clip.size[1]))
            z = "0" 
            line = "\t"+str(frame)+"\t"+x+"\t"+y+"\t"+"0"+"\n"
            
            data = data +line
        data = data + "\n"
        return data

    def write_cp_data_from_track(self,data):
        #print("WRITE_CP_DATA_FROM_TRACK Data: ",data)
        n_format = "{0:.3f}"
        for corner in range(4):
            
            AFXtx.write_afx_cp_keyframe_header(data,4,AFXtx.strings["corner_names"][corner])
            
            for marker in range(len(track.markers)):
                frame = track.markers[marker].frame
                x = str(n_format.format((track.markers[marker].co[0]+track.markers[marker].pattern_corners[corner][0])*clip.size[0]))
                y = str(n_format.format((1-(track.markers[marker].co[1]+track.markers[marker].pattern_corners[corner][1]))*clip.size[1]))
                line = "\t"+str(frame)+"\t"+x+"\t"+y+"\n"
                
                data = data +line
        data = data + "\n"  
        return data

AFXtx = AFX_Track_Exporter()
 
class TrackerExportPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "AFX Plane Track Exporter"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        
        clip = bpy.context.space_data.clip
        active_track = clip.tracking.tracks.active
        active_plane_track = clip.tracking.plane_tracks.active
        
        selected_plane_tracks = [pt for pt in clip.tracking.plane_tracks if pt.select == True]
        selected_tracks = [t for t in clip.tracking.tracks if t.select == True]
        
        if active_track != None or (active_plane_track != None and active_plane_track.select == True) :
            if active_track != None:
                row = layout.row()
                row.prop(active_track,"name")
                row.operator("wm.export_track_pos_only")
            if active_plane_track != None and active_plane_track.select == True:
                row = layout.row()
                row.prop(active_plane_track,"name")
                row.operator("wm.export_plane_track_cp_only")
        else:
            layout.label(text="Select a track or a plane Track to export")    
        
def init_file():
    data = ""
    #path = AFXtx.getFilePath()
    #file=open(path+"plane_tracks2.txt","w")    
    data = AFXtx.write_afx_keyframe_header(data,0)
    #return file
    return data

def finalize_file(data):
    #print("FINALIZE DATA: ", data)
    data = AFXtx.write_afx_keyframe_header(data,6)
    return data
    #file.close()
    
def export_track(context):
    
    clip = bpy.context.space_data.clip
    active_track = clip.tracking.tracks.active
    data = init_file()
    
    data = AFXtx.write_afx_keyframe_header(data,1)
    
    data = AFXtx.write_pos_from_single_track(data,active_track)
    
    data = finalize_file(data)
    
    bpy.context.window_manager.clipboard = data
    #print("FINAL DATA: \n\n", data)
    
def export_plane_track(context):
    
    clip = bpy.context.space_data.clip
    active_plane_track = clip.tracking.plane_tracks.active
    data = init_file()
    #data = AFXtx.write_afx_keyframe_header(data,1)
    data = AFXtx.write_cp_data(data,active_plane_track)
    data = finalize_file(data)
    
    bpy.context.window_manager.clipboard = data
    #print("FINAL DATA: \n\n", data)

class ExportTrack(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "wm.export_track_pos_only"
    bl_label = "export track"

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        export_track(context)
        return {'FINISHED'}

class ExportPlaneTrack(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "wm.export_plane_track_cp_only"
    bl_label = "export corner pin"
    test = bpy.props.BoolProperty(name="Execute",description="If it shall actually run, for optimal performance",default=False)

#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None

    def execute(self, context):
        export_plane_track(context)
        return {'FINISHED'}                

def register():
    bpy.utils.register_class(TrackerExportPanel)
    bpy.utils.register_class(ExportTrack)
    bpy.utils.register_class(ExportPlaneTrack)

def unregister():
    bpy.utils.unregister_class(TrackerExportPanel)
    bpy.utils.unregister_class(ExportTrack)
    bpy.utils.unregister_class(ExportPlaneTrack)

if __name__ == "__main__":
    register()

