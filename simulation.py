import polyfempy as pf
import pyvista as pv 
import pyvistaqt as pvqt
import json
import numpy as np
import os
import threading
import time
import sys

# FIXME better solution
os.environ["QT_QPA_PLATFORM"]="xcb"

class Sim:
    def __init__(self,object_json) -> None:
        self.asset_file = object_json
        with open(self.asset_file,'r') as f:
            self.config = json.load(f)
        self.step_count = 1
        self.solver = pf.Solver()
        self.solver.set_log_level(2)
        self.solver.set_settings(json.dumps(self.config))
        self.solver.load_mesh_from_settings()
        self.frame_time = self.config["time"]['dt']
        self.dt = self.frame_time
        self.solver.init_timestepping(self.config["time"]['dt'], self.frame_time)
        self.plotter = pvqt.BackgroundPlotter()
        self.plotter.camera_position = np.array([(0.0, 3.3543430868776536, 30.23866060008553),
                                                (0.0, 3.3543430868776536, 0.0),
                                                (0.0, 1.0, 0.0)])
        self.solver.step_in_time(0,self.frame_time,0)
        self.mesh = pv.read("step_0.vtu")
        self.plotter.add_mesh(self.mesh.warp_by_vector(inplace=True))
        self.plotter.add_slider_widget(lambda force: self.solver.update_neumann_boundary(1,[0,-force,0])
                                       , (1,max_force), 1, "Press Force")
        self.sim_thread = threading.Thread(target=self.run_simulation, daemon=True)
        self.sim_thread.start()
    
    def __del__(self):
        pass
        # os.remove("step_0.vtu")
        # os.remove("step_0.vtm")

    def run_simulation(self):
        while True:
            t = time.time()
            adj_dt = max(self.dt, self.frame_time)
            self.solver.step_in_time(0, adj_dt, 0)
            self.dt = time.time()-t
            self.plotter.add_text(f"TPS:{int(1/self.dt)}", name="tps")
            mesh: pv.UnstructuredGrid  = pv.read("step_0.vtu")
            self.mesh.points = mesh.warp_by_vector(inplace=True).points
            self.plotter.render()
            # self.plotter.add_mesh(mesh.warp_by_vector(), name="mesh")
            if self.frame_time>self.dt:
                time.sleep(self.frame_time-self.dt)
        
if __name__ == "__main__":
    if len(sys.argv)<2:
        print("format: simulation.py <configuration> <max_force_override(optional, default=10000)>")
    if len(sys.argv)<3:
        max_force = 10000
    else:
        max_force = int(sys.argv[2])
    s = Sim(sys.argv[1])
    input()
