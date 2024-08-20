bl_info = {
    "name": "Export PolyFEM",
    "blender": (4, 1, 0),
    "category": "Export",
}

import bpy
import json
from pathlib import Path
import os
import subprocess 

polyfem_json = json.loads("""{
    "geometry": [{
        "mesh": "./to_press.msh",
        "transformation": {
            "translation": [0, 1.1, 0],
            "rotation": [90,0,0],
            "scale": 1
        },
        "volume_selection": 1
    }, {
        "mesh": "mesh/press2.msh",
        "transformation": {
            "translation": [0, 5, 0],
            "rotation": [90,0,0],
            "scale": [1,1,1]
        },
        "surface_selection": 1,
        "volume_selection": 2
    },
    {
        "mesh": "mesh/press1.stl",
        "transformation": {
            "translation": [0, 5, 0],
            "rotation": [90,0,0],
            "scale": [1.01,1.01,1.01]
        },
        "volume_selection": 4,
        "is_obstacle":true
    },{
        "mesh": "mesh/plane.obj",
        "transformation": {
            "translation": [0, 0, 0]
        },
        "volume_selection": 3,
        "is_obstacle":true
    }],
    "contact": {
        "dhat": 1e-3
    },
    "time": {
        "tend": 1.0,
        "dt":0.042,
        "t0":0,
        "time_steps": 50
    },
    "boundary_conditions": {
        "rhs": [0, 9.81, 0],
        "neumann_boundary": [{
                "id": 1,
                "value": [
                    0,
                    -1e1,
                    0
                ]
            }]
    },
    "materials": [{
        "id": 1,
        "E": 5e6,
        "nu": 0.2,
        "rho": 5000,
        "type": "NeoHookean"
    },{
        "id": 2,
        "E": 1e13,
        "nu": 0.0,
        "rho": 0,
        "type": "NeoHookean"
    }],
    "contact": {
        "enabled": true,
        "dhat": 0.001
    },
    "solver": {
        "linear": {
            "solver": "Eigen::CholmodSupernodalLLT"
        },
        "nonlinear": {
            "line_search": {
                "method": "backtracking"
            },
            "solver": "newton",
            "x_delta": 1e-12,
            "grad_norm": 1
        },
        "contact":{
          "CCD":{
            "tolerance": 1
          }
        },
        "advanced": {
            "lump_mass_matrix": true
        }
    },
    "output": {
        "directory":"out",
        "json": "sim.json",
        "paraview": {
            "file_name": "sim.pvd",
            "options": {
                "material": false,
                "body_ids": false,
                "tensor_values": false,
                "discretization_order": false,
                "nodes": false,
                "high_order_mesh":true
            },
            "vismesh_rel_area": 10000000
        },
        "advanced": {
            "save_solve_sequence_debug": false,
            "save_time_sequence": true
        }
    }
}""")

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import FloatProperty, StringProperty
from bpy.types import Operator


class ExportPolyFEM(Operator, ExportHelper):
    """Export mesh to PolyFEM format"""
    bl_idname = "export_polyfem.export"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export PolyFEM data"

    # ExportHelper mix-in class uses this.
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    E_param: FloatProperty(
        name="E",
        description="E parameter",
        default=5e6,
    )

    nu_param: FloatProperty(
        name="nu",
        description="nu parameter",
        default=0.2,
    )

    rho_param: FloatProperty(
        name="rho",
        description="rho parameter",
        default=5000,
    )

    def execute(self, context):
        print("exporting to PolyFEM...")
        max_x=max_y=max_z=0
        for obj in bpy.data.objects:
            dim = obj.dimensions
            max_x = max(max_x,dim[0])
            max_y = max(max_y,dim[1])
            max_z = max(max_z,dim[2])
        print("Bounding Box: ",max_x,max_y,max_z)
        bpy.ops.wm.stl_export(filepath=os.path.join(Path(self.filepath).parent,"to_press.stl"))
        subprocess.run(["FloatTetwild_bin", "-i", "to_press.stl", "-o", "to_press.msh" ,"--max-threads", "12", "--coarsen", "-l", "1" ,"--use-floodfill", "--stop-energy", "100"])
        polyfem_json["materials"][0]["E"]=self.E_param
        polyfem_json["materials"][0]["nu"]=self.nu_param
        polyfem_json["materials"][0]["rho"]=self.rho_param
        polyfem_json["geometry"][0]["transformation"]["translation"]=[0,max_z/2+0.1,0]
        polyfem_json["geometry"][1]["transformation"]["translation"]=[0,max_z*2+1,0]
        polyfem_json["geometry"][2]["transformation"]["translation"]=[0,max_z*1.5+1,0]
        polyfem_json["geometry"][1]["transformation"]["scale"]=[max_x*0.6,max_y*0.6,max_z*0.3]
        polyfem_json["geometry"][2]["transformation"]["scale"]=[max_x*0.6+0.01,max_y*0.6+0.01, 1.01]
        polyfem_json["geometry"][3]["transformation"]["scale"]=[max_x/10+0.5,1,max_y/10+0.5]
        
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(polyfem_json, f, indent=2)
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportPolyFEM.bl_idname, text="Export to PolyFEM")


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(ExportPolyFEM)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_polyfem.export('INVOKE_DEFAULT')
