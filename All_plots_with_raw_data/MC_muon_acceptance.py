'''
In this script we simulate through a simple MC model the acceptance of our detector to atmospheric muons.
We assume a uniform distribution of muon entry points on a 2m x 2m plane above the detector, and a cos²θ angular distribution
for the muon directions.
We then check how many of these muons would intersect the detector volume, and from that we calculate the effective area and
compare it to the true geometric area of the detector.
'''

import numpy as np

# -----------------------------
# Detector geometry (in meters)
# -----------------------------
det_length = 1.65   # 165 cm
det_width  = 0.06   # 6 cm
det_height = 0.01   # 1 cm

# Detector centered at origin for convenience
det_xmin, det_xmax = -det_length/2, det_length/2
det_ymin, det_ymax = -det_width/2,  det_width/2
det_zmin, det_zmax = 0.0, det_height

# -----------------------------
# Simulation plane (2m × 2m)
# -----------------------------
plane_size = 2.0   # meters
A_sim = plane_size * plane_size

# -----------------------------
# Number of simulated muons
# -----------------------------
N = 2_000_000

# -----------------------------
# 1. Generate entry points uniformly on the plane
# -----------------------------
x0 = np.random.uniform(-plane_size/2, plane_size/2, N)
y0 = np.random.uniform(-plane_size/2, plane_size/2, N)
z0 = np.zeros(N)  # plane at z = 0

# -----------------------------
# 2. Generate directions with cos²θ distribution
# -----------------------------
# Sample cosθ from distribution f(cosθ) ∝ cos²θ on [0,1]
u = np.random.rand(N)
cos_theta = u**(1/3)      # inverse CDF of cos²θ we sample F not f
sin_theta = np.sqrt(1 - cos_theta**2)

phi = np.random.uniform(0, 2*np.pi, N)

dx = sin_theta * np.cos(phi)
dy = sin_theta * np.sin(phi)
dz = cos_theta

# -----------------------------
# 3. Compute intersection with detector volume
# -----------------------------
# Parametric line: r(t) = (x0, y0, z0) + t*(dx, dy, dz)
# Solve for t when z = det_zmin and z = det_zmax
t_enter = (det_zmin - z0) / dz
t_exit  = (det_zmax - z0) / dz

# Ensure t_enter < t_exit
t1 = np.minimum(t_enter, t_exit)
t2 = np.maximum(t_enter, t_exit)

# Compute intersection points
x1 = x0 + t1 * dx
y1 = y0 + t1 * dy

x2 = x0 + t2 * dx
y2 = y0 + t2 * dy

# Check if either intersection lies inside detector XY bounds
hit = (
    ((det_xmin <= x1) & (x1 <= det_xmax) &
     (det_ymin <= y1) & (y1 <= det_ymax)) |
    ((det_xmin <= x2) & (x2 <= det_xmax) &
     (det_ymin <= y2) & (y2 <= det_ymax))
)

N_acc = np.sum(hit)
fraction = N_acc / N

# -----------------------------
# 4. Effective area
# -----------------------------
A_eff = fraction * A_sim
A_geom = det_length * det_width

print(f"\nSimulated events: {N}")
print(f"Accepted events:  {N_acc}")
print(f"Acceptance fraction: {fraction:.5f}")
print(f"Effective area: {A_eff:.4f} m²")
print(f"True geometric area: {A_geom:.4f} m²")
print(f"Ratio A_eff / A_geom = {A_eff / A_geom:.3f}\n")
