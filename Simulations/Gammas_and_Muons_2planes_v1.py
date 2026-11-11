"""
Optimized Muon + Gamma energy deposition simulation using Numba.
Requires: numpy, numba, matplotlib.
"""

from matplotlib.pylab import default_rng
from matplotlib.pylab import SeedSequence
import numpy as np
import matplotlib.pyplot as plt
from numba import njit

# ============================================================
# Constants & Geometry
# ============================================================
MEC2 = 0.510998950       # MeV
M_MU = 0.10566 # mass of muon in MeV
R0   = 2.8179403262e-13  # cm
ED_EJ200 = 3.33e23       # electrons / cm^3

# Geometry (cm)
L_SC, H_SC, W_SC = 169.0, 6.0, 1.0
GAP = 4.0
DET_AREA   = L_SC * H_SC

# This is for the MC generation of muons, we generate them in an area bigger than detector
MC_L, MC_H = L_SC, H_SC
# This is for the MC generation of gammas, we generate them in a circle with this radius
MC_R = 5.0 * L_SC


# Bounding boxes: [xmin, xmax, ymin, ymax, zmin, zmax]
BOX_BOTTOM = np.array([-L_SC/2, L_SC/2, -H_SC/2, H_SC/2, 0.0, W_SC])
BOX_TOP    = np.array([-L_SC/2, L_SC/2, -H_SC/2, H_SC/2, W_SC + GAP, 2*W_SC + GAP])
Z_GEN = BOX_TOP[5] + 0.0

# Time per seed
T_PER_SEED  = 1.0          

# Physics parameters
DEDX_MPV   = 2.0         # MeV/cm for muons in plastic
DEDX_WIDTH = 0.3         # Landau width
GAMMA_ALPHA, GAMMA_EMIN, GAMMA_EMAX = 2.0, 0.1, 4.0
THRESHOLD   = 0.01       
MUON_FLUX  = 0.02        
GAMMA_FLUX = 1.0         
T_MEAS     = 3600.0

# Muon energy distribution parameters for Gaisser formula
E_MIN_MU, E_MAX_MU = 1.0, 500.0
# Overburden parameters
A_OVERBURDEN, ALPHA_OVERBURDEN = 2.5, 0.8

# --- Overburden Parameters ---
ROCK_OVERBURDEN_MWE = 0.0 # Meters Water Equivalent (m.w.e).
# (Set to 0.0 for sea level)

#random number generator
MASTER_SEED = 20260513

# ============================================================
# Numba Helpers
# ============================================================
@njit
def ray_box_intersection(origin, direction, box):
    t_min, t_max = -1e9, 1e9
    for i in range(3):
        bmin = box[2*i]
        bmax = box[2*i+1]
        if abs(direction[i]) < 1e-12:
            if origin[i] < bmin or origin[i] > bmax:
                return False, 0.0, 0.0
        else:
            t1 = (bmin - origin[i]) / direction[i]
            t2 = (bmax - origin[i]) / direction[i]
            if t1 > t2:
                t1, t2 = t2, t1
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)
    if t_max <= max(t_min, 0.0):
        return False, 0.0, 0.0
    return True, max(t_min, 0.0), t_max

@njit
def sample_landau_energy_loss(path, E_muon_GeV):
    mpv_base = DEDX_MPV * path
    
    gamma = max(E_muon_GeV / M_MU, 1.0)
    beta = np.sqrt(1.0 - 1.0 / (gamma**2))
    
    energy_correction = 1.0 / (beta**2)
    energy_correction = min(energy_correction, 2.5) 
    
    mpv = mpv_base * energy_correction
    scale = DEDX_WIDTH * np.sqrt(path) * energy_correction
    
    u = np.random.rand()
    val = mpv + scale * (-1.0 + u / (1.0 - u))
    return max(val, THRESHOLD)

@njit
def scattered_energy(E0, theta):
    x = E0 / MEC2
    return E0 / (1.0 + x * (1.0 - np.cos(theta)))

@njit
def dSigmaKN_dOmega(E0, theta):
    Ep    = scattered_energy(E0, theta)
    ratio = Ep / E0
    s2    = np.sin(theta) ** 2
    return 0.5 * R0**2 * ratio**2 * (ratio + 1.0 / ratio - s2)

@njit
def sigmaKN_total(E0):
    x = E0 / MEC2
    l = np.log(1.0 + 2.0 * x)
    term1 = ((1.0 + x) / x**2) * (2.0 * (1.0 + x) / (1.0 + 2.0 * x) - l / x)
    term2 = l / (2.0 * x)
    term3 = (1.0 + 3.0 * x) / (1.0 + 2.0 * x)**2
    return 2.0 * np.pi * R0**2 * (term1 + term2 - term3)

@njit
def mu_compton(E0):
    return ED_EJ200 * sigmaKN_total(E0)

@njit
def sample_kn_theta(E0):
    max_dsig = dSigmaKN_dOmega(E0, 0.0)
    while True:
        ct    = np.random.rand() * 2.0 - 1.0
        theta = np.arccos(ct)
        if np.random.rand() * max_dsig < dSigmaKN_dOmega(E0, theta):
            return theta

@njit
def rotate_direction(d, theta, phi):
    norm = np.sqrt(d[0]**2 + d[1]**2 + d[2]**2)
    d = d / norm
    if abs(d[2]) < 0.9:
        perp1 = np.cross(d, np.array([0.0, 0.0, 1.0]))
    else:
        perp1 = np.cross(d, np.array([1.0, 0.0, 0.0]))
    perp1 /= np.sqrt(perp1[0]**2 + perp1[1]**2 + perp1[2]**2)
    perp2 = np.cross(d, perp1)
    nd = (np.cos(theta) * d
          + np.sin(theta) * np.cos(phi) * perp1
          + np.sin(theta) * np.sin(phi) * perp2)
    return nd / np.sqrt(nd[0]**2 + nd[1]**2 + nd[2]**2)

# ============================================================
# Numba Core Loops
# ============================================================
@njit
def track_muon_numba(mu_x, mu_y, mu_ct, mu_st, mu_phi, mu_E, n_muons, overburden_mwe):
    muon_Edep_top_bar = np.zeros(n_muons)
    muon_Edep_bottom_bar = np.zeros(n_muons)

    for i in range(n_muons):
        E_initial = mu_E[i]
        path_length_rock = overburden_mwe / mu_ct[i]
        range_rock = A_OVERBURDEN * (E_initial ** ALPHA_OVERBURDEN) 
        
        if range_rock < path_length_rock:
            continue
            
        E_surviving = ( (range_rock - path_length_rock) / 2.5 ) ** (1.0 / 0.8)
        
        if E_surviving < 0.1:
            continue

        direction = np.array([mu_st[i]*np.cos(mu_phi[i]), mu_st[i]*np.sin(mu_phi[i]), -mu_ct[i]])
        origin = np.array([mu_x[i], mu_y[i], Z_GEN])

        hit_top, t0_top, t1_top = ray_box_intersection(origin, direction, BOX_TOP)
        hit_bot, t0_bot, t1_bot = ray_box_intersection(origin, direction, BOX_BOTTOM)

        if hit_top and hit_bot:
            path_top = t1_top - t0_top
            path_bot = t1_bot - t0_bot
            
            E_dep_top = sample_landau_energy_loss(path_top, E_surviving)
            E_dep_bot = sample_landau_energy_loss(path_bot, E_surviving)
            
            if E_dep_top > THRESHOLD:
                muon_Edep_top_bar[i] = E_dep_top
            if E_dep_bot > THRESHOLD:
                muon_Edep_bottom_bar[i] = E_dep_bot

    return muon_Edep_top_bar, muon_Edep_bottom_bar

@njit
def track_gamma_numba(g_pos_x, g_pos_y, g_pos_z, g_dir_x, g_dir_y, g_dir_z, g_E, n_gammas):
    gamma_Edep_top_bar = np.zeros(n_gammas)
    gamma_Edep_bottom_bar = np.zeros(n_gammas)

    for i in range(n_gammas):
        pos  = np.array([g_pos_x[i], g_pos_y[i], g_pos_z[i]])
        dirn = np.array([g_dir_x[i], g_dir_y[i], g_dir_z[i]])
        E = g_E[i]
        
        bars_hit_top = False
        bars_hit_bot = False
        E_sum_top = 0.0
        E_sum_bottom = 0.0

        for _ in range(8):
            best_bar = -1
            best_t_enter = 1e9
            best_t_exit = 0.0

            hit_bot, t0_b, t1_b = ray_box_intersection(pos, dirn, BOX_BOTTOM)
            if hit_bot and t0_b < best_t_enter:
                best_t_enter, best_t_exit = t0_b, t1_b
                best_bar = 0

            hit_top, t0_t, t1_t = ray_box_intersection(pos, dirn, BOX_TOP)
            if hit_top and t0_t < best_t_enter:
                best_t_enter, best_t_exit = t0_t, t1_t
                best_bar = 1

            if best_bar == -1: break

            path = best_t_exit - best_t_enter
            mu = mu_compton(E)
            p_int = 1.0 - np.exp(-mu * path)

            if np.random.rand() > p_int:
                pos = pos + (best_t_exit + 0.01) * dirn
                continue

            u = np.random.rand()
            d_int = -np.log(1.0 - u * (1.0 - np.exp(-mu * path))) / mu
            ipos = pos + (best_t_enter + d_int) * dirn

            theta = sample_kn_theta(E)
            E_prime = scattered_energy(E, theta)
            E_dep = E - E_prime

            if best_bar == 0 and E_dep > THRESHOLD: 
                E_sum_bottom += E_dep
                bars_hit_bot = True
            elif best_bar == 1 and E_dep > THRESHOLD:
                E_sum_top += E_dep
                bars_hit_top = True

            if E_prime < THRESHOLD: break

            phi = np.random.rand() * 2.0 * np.pi
            dirn = rotate_direction(dirn, theta, phi)
            pos = ipos + 0.01 * dirn
            E = E_prime

        if bars_hit_top and bars_hit_bot:
            gamma_Edep_top_bar[i] = E_sum_top
            gamma_Edep_bottom_bar[i] = E_sum_bottom

    return gamma_Edep_top_bar, gamma_Edep_bottom_bar

# ============================================================
# Python Wrappers
# ============================================================
def generate_muons(n_target, rng):
    n_gen = n_target*10
    ct = rng.uniform(0.0, 1.0, n_gen) ** (1.0/3.0)
    theta = np.arccos(ct)
    phi = rng.uniform(0.0, 2.0 * np.pi, n_gen)
    st = np.sin(theta)

    x_flat = rng.uniform(-MC_L, MC_L, n_gen)
    y_flat = rng.uniform(-MC_H, MC_H, n_gen)

    x_det = x_flat - Z_GEN * (st / ct) * np.cos(phi)
    y_det = y_flat - Z_GEN * (st / ct) * np.sin(phi)

    mask = ((BOX_TOP[0] <= x_det) & (x_det <= BOX_TOP[1]) & (BOX_TOP[2] <= y_det) & (y_det <= BOX_TOP[3]))
    
    ct_hit = ct[mask][:n_target]
    st_hit = st[mask][:n_target]
    phi_hit = phi[mask][:n_target]
    x_hit = x_flat[mask][:n_target]
    y_hit = y_flat[mask][:n_target]

    # --- Actual number of muons that hit the detector ---
    n_actual = len(ct_hit)
    if n_actual == 0:
        return (x_hit, y_hit, ct_hit, st_hit, phi_hit, np.array([]))
    
    cos_theta = np.maximum(ct_hit, 0.087)
    
    term1 = 0.14 * (E_MIN_MU ** -2.7)
    num1  = 1.0 / (1.0 + (1.1 * E_MIN_MU * cos_theta) / 115.0)
    num2  = 0.054 / (1.0 + (1.1 * E_MIN_MU * cos_theta) / 850.0)
    max_pdf = term1 * (num1 + num2) * 1.1

    E_muon = np.zeros(n_actual)
    accepted = np.zeros(n_actual, dtype=bool)
    
    while not np.all(accepted):
        # Use n_actual instead of n_target
        n_rem = n_actual - np.sum(accepted)
        idx_rem = np.where(~accepted)[0]
        
        E_cand = rng.uniform(E_MIN_MU, E_MAX_MU, n_rem)
        cos_th_cand = cos_theta[idx_rem]
        
        term1_cand = 0.14 * (E_cand ** -2.7)
        num1_cand  = 1.0 / (1.0 + (1.1 * E_cand * cos_th_cand) / 115.0)
        num2_cand  = 0.054 / (1.0 + (1.1 * E_cand * cos_th_cand) / 850.0)
        pdf_cand = term1_cand * (num1_cand + num2_cand)
        
        accept_mask = rng.uniform(0, max_pdf[idx_rem]) < pdf_cand
        E_muon[idx_rem[accept_mask]] = E_cand[accept_mask]
        accepted[idx_rem[accept_mask]] = True

    return (x_hit, y_hit, ct_hit, st_hit, phi_hit, E_muon)

@njit
def _filter_gammas_hitting(pos_x, pos_y, pos_z, dir_x, dir_y, dir_z, n_target):
    idx_out = np.empty(n_target, dtype=np.int64)
    count = 0
    for i in range(len(pos_x)):
        origin    = np.array([pos_x[i], pos_y[i], pos_z[i]])
        direction = np.array([dir_x[i], dir_y[i], dir_z[i]])
        hb, _, _ = ray_box_intersection(origin, direction, BOX_BOTTOM)
        ht, _, _ = ray_box_intersection(origin, direction, BOX_TOP)
        if hb or ht:
            idx_out[count] = i
            count += 1
            if count == n_target: break
    return idx_out[:count]

def generate_gammas(n_target, rng):

    p_hit = (L_SC * H_SC) / (np.pi * MC_R**2)
    n_gen = int(n_target / p_hit * 2.0)

    E = (GAMMA_EMIN**(1 - GAMMA_ALPHA) + rng.uniform(0, 1, n_gen)
         * (GAMMA_EMAX**(1 - GAMMA_ALPHA) - GAMMA_EMIN**(1 - GAMMA_ALPHA))
         ) ** (1.0 / (1.0 - GAMMA_ALPHA))

    ct    = rng.uniform(-1.0, 1.0, n_gen)
    st    = np.sqrt(1.0 - ct**2)
    phi   = rng.uniform(0.0, 2.0 * np.pi, n_gen)
    dx    = st * np.cos(phi)
    dy    = st * np.sin(phi)
    dz    = ct

    cx, cy, cz = BOX_TOP[0] + (BOX_TOP[1] - BOX_TOP[0]) / 2, BOX_TOP[2] + (BOX_TOP[3] - BOX_TOP[2]) / 2, BOX_TOP[4] + (BOX_TOP[5] - BOX_TOP[4]) / 2
    pos_x = cx + MC_R * dx
    pos_y = cy + MC_R * dy
    pos_z = cz + MC_R * dz

    idx = _filter_gammas_hitting(pos_x, pos_y, pos_z, -dx, -dy, -dz, n_target)

    return (pos_x[idx], pos_y[idx], pos_z[idx], -dx[idx], -dy[idx], -dz[idx], E[idx])

# ============================================================
# Simulation of 1 second of data
# ============================================================
def simulate_1second(chunk_index, master_seed=MASTER_SEED):
    ss_np = SeedSequence(master_seed, spawn_key=(chunk_index, 0))
    rng   = default_rng(ss_np)

    ss_nb = SeedSequence(master_seed, spawn_key=(chunk_index, 1))
    np.random.seed(int(ss_nb.generate_state(1)[0]))

    n_muon  = int(MUON_FLUX  * (MC_H*MC_L) * T_PER_SEED)
    n_gamma = int(GAMMA_FLUX * DET_AREA * T_PER_SEED)

    mx, my, mct, mst, mphi, mE = generate_muons(n_muon, rng)
    gx, gy, gz, gdx, gdy, gdz, gE = generate_gammas(n_gamma, rng)

    muon_Edep_top_bar, muon_Edep_bottom_bar = track_muon_numba(mx, my, mct, mst, mphi, mE, len(mx), ROCK_OVERBURDEN_MWE)
    gamma_Edep_top_bar, gamma_Edep_bottom_bar = track_gamma_numba(gx, gy, gz, gdx, gdy, gdz, gE, len(gx))

    return (muon_Edep_top_bar, muon_Edep_bottom_bar, gamma_Edep_top_bar, gamma_Edep_bottom_bar, n_muon, n_gamma)

# ============================================================
# Main
# ============================================================
def main():
    muon_Edep_top_bar, muon_Edep_bottom_bar, gamma_Edep_top_bar, gamma_Edep_bottom_bar, N_muons, N_gammas = [], [], [], [], [], []

    print(f"Simulating {T_MEAS}s...")
    n_chunks = int(np.ceil(T_MEAS/T_PER_SEED))
    for chunk_index in range(n_chunks):
        print(f"\n--- Chunk {chunk_index+1}/{n_chunks} ---")
        
        muon_Edep_top_bar_aux, muon_Edep_bottom_bar_aux, gamma_Edep_top_bar_aux, gamma_Edep_bottom_bar_aux, n_muon_aux, n_gamma_aux = simulate_1second(chunk_index)
        
        # Filter out zeros and extend lists
        muon_Edep_top_bar.extend(muon_Edep_top_bar_aux[muon_Edep_top_bar_aux > 0])
        muon_Edep_bottom_bar.extend(muon_Edep_bottom_bar_aux[muon_Edep_bottom_bar_aux > 0])
        gamma_Edep_top_bar.extend(gamma_Edep_top_bar_aux[gamma_Edep_top_bar_aux > 0])
        gamma_Edep_bottom_bar.extend(gamma_Edep_bottom_bar_aux[gamma_Edep_bottom_bar_aux > 0])
        N_muons.append(n_muon_aux)
        N_gammas.append(n_gamma_aux)

    print(f"Generating {sum(N_muons)} muons and {sum(N_gammas)} gammas.\n")
    print(f"Total simulation time: {T_MEAS}.")

    fig, axes = plt.subplots(1, 2, figsize=(15, 8))
    bins_all = np.linspace(0, 5.0, 100)

    def plot_with_errors(ax, data, color, label):
        if len(data) == 0:
            return
        counts, bin_edges = np.histogram(data, bins=bins_all)
        centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        dx      = bin_edges[1] - bin_edges[0]

        density     = counts / (len(data) * dx)
        density_err = np.sqrt(counts) / (len(data) * dx)

        # "mid" step: flat segment centred on each bin centre → aligns with errorbar markers
        ax.step(centers, density, where='mid', color=color, lw=1.5, label=label)

        mask = counts > 0
        ax.errorbar(centers[mask], density[mask], yerr=density_err[mask],
                    fmt='none', ecolor=color, capsize=2, alpha=0.6)

    def get_rate_str(n_events, time):
        if n_events == 0: return "0.00 ± 0.00 Hz"
        return f"{n_events/time:.2f} ± {np.sqrt(n_events)/time:.2f} Hz"

    plot_with_errors(axes[0], muon_Edep_top_bar, 'C0', 'Muon PDF')
    plot_with_errors(axes[0], gamma_Edep_top_bar, 'C1', 'Gamma PDF')
    axes[0].set_title(f"Top bar (2-bar coincidences)\n"
                      f"μ: {get_rate_str(len(muon_Edep_top_bar), T_MEAS)}\n"
                      f"γ: {get_rate_str(len(gamma_Edep_top_bar), T_MEAS)}")
    axes[0].set_xlabel("E_dep top bar (MeV)")
    axes[0].set_ylabel("Probability density")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    plot_with_errors(axes[1], muon_Edep_bottom_bar, 'C0', 'Muon PDF')
    plot_with_errors(axes[1], gamma_Edep_bottom_bar, 'C1', 'Gamma PDF')
    axes[1].set_title(f"Bottom bar (2-bar coincidences)\n"
                      f"μ: {get_rate_str(len(muon_Edep_bottom_bar), T_MEAS)}\n"
                      f"γ: {get_rate_str(len(gamma_Edep_bottom_bar), T_MEAS)}")
    axes[1].set_xlabel("E_dep bottom bar (MeV)")
    axes[1].set_ylabel("Probability density")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    plt.tight_layout()
    plt.show()
    fig.savefig(r".\Simulations\Plots\GammasMuons_2BarsCoin.png", dpi=300, bbox_inches="tight")
    plt.close()

if __name__ == "__main__":
    main()