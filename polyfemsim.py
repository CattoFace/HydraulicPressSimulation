import polyfempy as pf
import json
import numpy as np

class Sim:
    def __init__(self) -> None:
        self.asset_file = 'python_press.json'
        with open(self.asset_file,'r') as f:
            self.config = json.load(f)
        self.step_count = 1
        self.solver = pf.Solver()
        self.solver.set_log_level(2)
        breakpoint()
        self.solver.set_settings(json.dumps(self.config))
        self.solver.load_mesh_from_settings()
        self.cumulative_action = np.zeros(3)
        self.dt = self.config["time"]['dt']
        self.t0 = self.config["time"]["t0"]
        self.solver.init_timestepping(self.t0, self.dt)
        # self.id_to_mesh = {}
        # self.id_to_position = {}
        # self.id_to_vf = {}
        # for mesh in self.config["geometry"]:
        #     self.id_to_mesh[mesh["volume_selection"]] = mesh["mesh"]
        #     self.id_to_position[mesh["volume_selection"]] = mesh["transformation"]["translation"]
            
    def set_boundary_conditions(self):
        t0 = self.t0
        t1 = t0 + self.dt
        self.solver.update_dirichlet_boundary(
            2,
            [
                "0",
                "1.25*t",
                "0"
            ]
        )
        # self.cumulative_action += action
        
    # def get_object_positions(self):
    #     points, tets, _, body_ids, displacement = self.solver.get_sampled_solution()
    #     self.id_to_position = {}
    #     self.id_to_vertex = {}
    #     for mesh_id, _ in self.id_to_mesh.items():
    #         vertex_position = points + displacement
    #         self.id_to_vertex[mesh_id] = vertex_position[body_ids[:,0]==mesh_id]
    #         mean_cell_id = np.mean(body_ids[tets], axis=1).astype(np.int32).flat
    #         tet_barycenter = np.mean(vertex_position[tets], axis=1)
    #         self.id_to_position[mesh_id] = np.mean(tet_barycenter[mean_cell_id == mesh_id], axis=0)
    #     return self.id_to_position
    #
    def run_simulation(self):
        self.solver.step_in_time(0, self.dt, self.step_count)
        self.step_count += 1
        self.t0 += self.dt
        
    def step(self):
        # self.set_boundary_conditions()
        self.run_simulation()
        # return self.get_object_positions()
