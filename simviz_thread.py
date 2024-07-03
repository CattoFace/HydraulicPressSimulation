import polyfempy as pf
import pyvista as pv 
import pyvistaqt as pvqt
import json
import numpy as np
import os
import threading
import time

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
        self.frame_time = 1/24
        self.plotter.camera_position = np.array([(0.0, 3.3543430868776536, 30.23866060008553),
                                                (0.0, 3.3543430868776536, 0.0),
                                                (0.0, 1.0, 0.0)])
        self.plotter.add_slider_widget(lambda force: self.solver.update_neumann_boundary(1,[0,-force,0])
                                       , (1,10000), 1, "Press Force")
        self.sim_thread = threading.Thread(target=self.run_simulation, daemon=True)
        self.sim_thread.start()
        self.lock = threading.Lock()
    
    def __del__(self):
        os.remove("step_0.vtu")
        os.remove("step_0.vtm")

    def update_density(self, new_density):
        self.solver.update_neumann_boundary(1,[0,-new_density,0])
            
    def run_simulation(self):
        while True:
            t = time.time()
            self.solver.step_in_time(0, max(self.dt,self.frame_time), 0)
            self.dt = time.time()-t
            mesh: pv.UnstructuredGrid  = pv.read("step_0.vtu")
            self.plotter.add_mesh(mesh.warp_by_vector(), name="mesh")
            self.step_count += 1
            self.t0 += self.dt
        
if __name__ == "__main__":
    s = Sim()
    input()
