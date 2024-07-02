import polyfempy as pf
import pyvista as pv 
import pyvistaqt as pvqt
import json
import numpy as np
import os

# FIXME better solution
os.environ["QT_QPA_PLATFORM"]="xcb"

class Sim:
    def __init__(self) -> None:
        self.asset_file = 'python_press.json'
        with open(self.asset_file,'r') as f:
            self.config = json.load(f)
        self.step_count = 1
        self.solver = pf.Solver()
        self.solver.set_log_level(2)
        self.solver.set_settings(json.dumps(self.config))
        self.solver.load_mesh_from_settings()
        self.cumulative_action = np.zeros(3)
        self.dt = self.config["time"]['dt']
        self.t0 = self.config["time"]["t0"]
        self.solver.init_timestepping(self.t0, self.dt)
        self.plotter = pvqt.BackgroundPlotter()
        self.plotter.camera_position = np.array([(0.0, 3.3543430868776536, 30.23866060008553),
                                                (0.0, 3.3543430868776536, 0.0),
                                                (0.0, 1.0, 0.0)])
        self.plotter.add_slider_widget(self.update_density, (1,10000), 1, "Press Density")
        self.plotter.add_callback(self.run_simulation, int(1000/24))

    def update_density(self, new_density):
        self.solver.update_neumann_boundary(1,[0,-new_density,0])
    #     self.config["materials"][1]["rho"]=10**new_density
    #     self.solver.settings(json.dumps(self.config))
    #     self.solver.load_mesh_from_settings()
    #     self.solver.init_timestepping(self.t0,self.dt)
    #     print(new_density)
            
    def run_simulation(self):
        self.solver.step_in_time(0, self.dt, self.step_count)
        mesh: pv.UnstructuredGrid  = pv.read(f"step_{self.step_count-1}.vtu")
        self.plotter.clear_actors()
        self.plotter.add_mesh(mesh.warp_by_vector())
        self.step_count += 1
        self.t0 += self.dt
        
    def step(self):
        # self.set_boundary_conditions()
        self.run_simulation()
        # return self.get_object_positions()
        #
if __name__ == "__main__":
    s = Sim()
    input()
