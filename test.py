from polyfemsim import Sim

env = Sim()

# push forward
for i in range(50):
    env.step()
