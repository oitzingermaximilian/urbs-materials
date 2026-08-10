import gurobipy as gp

print("Loading Pyomo's debug model...")
# Read the file you just generated
m = gp.read("my_debug_model.lp")

print("Running Gurobi Presolve...")
# Force Gurobi to mathematically simplify it
p = m.presolve()

print("Saving the surviving matrix...")
# Write the surviving math to a new file
p.write("presolved_model.lp")

print("Done! Open presolved_model.lp to see what survived.")