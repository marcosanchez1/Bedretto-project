"""
Gamma + Muon background simulation for a two-bar scintillator detector.

Physics implemented
-------------------
- Muons : Gaisser formula (energy depends on zenith angle), Landau dE/dx
- Gammas: E^-2 spectrum [0.1, 4] MeV, Compton (Klein-Nishina) with multiple
          scattering, isotropic generation over 4π.
- Light : exponential attenuation, 16 cm/ns propagation, Poisson fluctuations
- SiPMs : bottom bar -> 2 (both ends), top bar -> 1 (at x = 0)
- Coincidence: 15 ns window, threshold on photoelectrons

Generation Volume
-----------------
Particles are generated over a square area of side `2 * MC_LENGTH`.
Rates are scaled so that the flux *incident on the detector* remains physical.
"""

import numpy as np
import matplotlib.pyplot as plt

try:
    from scipy.stats import landau as _landau
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False

# ============================================================
# Constants
# ============================================================
MEC2       = 0.510998950          # MeV
R0         = 2.8179403262e-13     # cm
ED_EJ200   = 3.33e23              # electrons / cm^3

# ---- Geometry (cm) -----------------------------------------
L_SC, A_SC, W_SC = 169.0, 6.0, 1.0
GAP              = 4.0            # air gap between the two bars

MC_LENGTH = 5 * L_SC              # Generate points over a 2D square of side 2*MC_LENGTH

# ---- Light transport ---------------------------------------
LAMBDA_ATT   = 400.0              # effective attenuation length (cm), 4m according to spec sheet of EJ200
LIGHT_SPEED  = 16.0               # cm / ns in EJ200, this is what we've measured
EFF_YIELD    = 10000.0             # photoelectrons / MeV at SiPM this according to spec sheet
TIME_JITTER  = 0.5                # ns (SiPM + electronics)

# ---- Detection ---------------------------------------------
THRESHOLD    = 150                 # photoelectrons
COIN_WINDOW  = 15.0               # ns

# ---- Rates (1 s of data) -----------------------------------
MUON_FLUX    = 0.02               # Hz / cm^2 (vertical equivalent)
GAMMA_FLUX   = 2.55               # Hz / cm^2 (gives ~2586 gammas on detector)
DET_AREA     = L_SC * A_SC        # cm^2
T_MEAS       = 60.0                # s

# ---- Spectra -----------------------------------------------
GAMMA_ALPHA, GAMMA_EMIN, GAMMA_EMAX = 2.0, 0.1, 4.0
DEDX_MPV     = 2.0                # MeV/cm for MIP in plastic
DEDX_WIDTH   = 0.3                # Landau width (MeV/cm)

# ============================================================
# Geometry helpers
# ============================================================
# Let's put the bars's center at 0
BARS = {
    'bottom': {'min': np.array([-L_SC/2, -A_SC/2, 0.0]),
               'max': np.array([L_SC/2,  A_SC/2, W_SC])},
    'top':    {'min': np.array([-L_SC/2, -A_SC/2, W_SC + GAP]),
               'max': np.array([L_SC/2,  A_SC/2, 2*W_SC + GAP])},
}

SIPMS = {
    'bottom': [-L_SC/2, L_SC/2],   # two ends
    'top':    [L_SC/2],          # single SiPM at x = 0
}

# The virtual plane where we generate our particles
Z_GEN = BARS['top']['max'][2] + 5.0 

# ============================================================
# Physics: Klein-Nishina
# ============================================================
def scattered_energy(E0, theta):
    x = E0 / MEC2
    return E0 / (1.0 + x * (1.0 - np.cos(theta)))

def dSigmaKN_dOmega(E0, theta):
    Ep    = scattered_energy(E0, theta)
    ratio = Ep / E0
    s2    = np.sin(theta) ** 2
    return 0.5 * R0**2 * ratio**2 * (ratio + 1.0 / ratio - s2)

def sigmaKN_total(E0):
    x = E0 / MEC2
    l = np.log(1.0 + 2.0 * x)
    term1 = ((1.0 + x) / x**2) * (2.0 * (1.0 + x) / (1.0 + 2.0 * x) - l / x)
    term2 = l / (2.0 * x)
    term3 = (1.0 + 3.0 * x) / (1.0 + 2.0 * x)**2
    return 2.0 * np.pi * R0**2 * (term1 + term2 - term3)

def mu_compton(E0):
    return ED_EJ200 * sigmaKN_total(E0)

def sample_kn_theta(E0, rng):
    max_dsig = dSigmaKN_dOmega(E0, 0.0)
    while True:
        ct    = rng.uniform(-1.0, 1.0)
        theta = np.arccos(ct)
        if rng.uniform(0.0, max_dsig) < dSigmaKN_dOmega(E0, theta):
            return theta

# ============================================================
# Physics: Gaisser Formula for Muons
# ============================================================
def gaisser_dI_dE(E, theta, E_min=1.0, E_max=500.0):
    """
    Differential muon intensity (dI/dE) based on the Gaisser formula.
    E in GeV. theta in radians (0 = vertical).
    Only valid for E > 1 GeV.
    """
    # Ensure we don't evaluate below E_min
    E = np.maximum(E, E_min)
    cos_theta = np.cos(theta)
    
    # To avoid unphysical divergence at the horizon, we cap theta to e.g. 85 deg (cos_theta ~ 0.087)
    # typical for these parameterizations.
    cos_theta = np.maximum(cos_theta, 0.087)
    
    term1 = 0.14 * (E ** -2.7)
    num1  = 1.0 / (1.0 + (1.1 * E * cos_theta) / 115.0)
    num2  = 0.054 / (1.0 + (1.1 * E * cos_theta) / 850.0)
    
    return term1 * (num1 + num2)

def sample_gaisser_energy(theta, rng, E_min=1.0, E_max=500.0):
    """
    Rejection sampling for muon energy based on Gaisser formula.
    """
    # Find the maximum of the pdf within the range to use for rejection.
    # The peak of the E^-2.7 spectrum is at E_min.
    max_pdf = gaisser_dI_dE(E_min, theta, E_min, E_max) * 1.1 # 10% headroom
    
    while True:
        E = rng.uniform(E_min, E_max)
        p = gaisser_dI_dE(E, theta, E_min, E_max)
        if rng.uniform(0, max_pdf) < p:
            return E

# ============================================================
# General Sampling Helpers
# ============================================================
def sample_power_law(n, rng, alpha, E_min, E_max):
    u = rng.uniform(0.0, 1.0, n)
    a = 1.0 - alpha
    return (E_min**a + u * (E_max**a - E_min**a)) ** (1.0 / a)

def sample_landau_energy_loss(path, rng):
    mpv   = DEDX_MPV * path
    scale = DEDX_WIDTH * np.sqrt(path)
    if _HAS_SCIPY:
        val = _landau.rvs(loc=mpv, scale=scale, random_state=rng)
    else:
        val = rng.normal(mpv, scale)
    return max(val, 0.05 * mpv)

# ============================================================
# Geometry Intersections
# ============================================================
def ray_box_intersection(origin, direction, box):
    t_min, t_max = -np.inf, np.inf
    for i in range(3):
        if abs(direction[i]) < 1e-12:
            if origin[i] < box['min'][i] or origin[i] > box['max'][i]:
                return None
        else:
            t1 = (box['min'][i] - origin[i]) / direction[i]
            t2 = (box['max'][i] - origin[i]) / direction[i]
            if t1 > t2:
                t1, t2 = t2, t1
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)
    if t_max <= max(t_min, 0.0):
        return None
    return (max(t_min, 0.0), t_max)

def rotate_direction(d, theta, phi):
    d = d / np.linalg.norm(d)
    if abs(d[2]) < 0.9:
        perp1 = np.cross(d, [0.0, 0.0, 1.0])
    else:
        perp1 = np.cross(d, [1.0, 0.0, 0.0])
    perp1 /= np.linalg.norm(perp1)
    perp2 = np.cross(d, perp1)
    nd = (np.cos(theta) * d
          + np.sin(theta) * np.cos(phi) * perp1
          + np.sin(theta) * np.sin(phi) * perp2)
    return nd / np.linalg.norm(nd)

# ============================================================
# Muon generation / tracking
# ============================================================
def generate_muons(n_target, rng):
    """
    Generates muons over a wide area using Gaisser formula. 
    Coordinates are adjusted so the muon hits the Z_GEN plane.
    """
    # The flux decreases at large angles, so to get n_target hits we need to generate more.
    # We generate a batch and filter.
    generated = []
    
    # We sample over a larger flat area. 
    while len(generated) < n_target:
        # Sample angle: cos^2(theta) distribution
        ct = rng.uniform(0.0, 1.0) ** (1.0/3.0)
        theta = np.arccos(ct)
        
        # To hit the detector from angle theta, the intersection at Z_GEN must be offset.
        # We sample a flat distribution over the MC area.
        x_flat = rng.uniform(-MC_LENGTH, MC_LENGTH)
        y_flat = rng.uniform(-MC_LENGTH, MC_LENGTH)
        
        # Check if this ray actually hits the detector (simplification for generating)
        # The ray originates at (x_flat, y_flat) at height Z_GEN.
        # At z=0, x_actual = x_flat - Z_GEN * tan(theta) * cos(phi)
        phi = rng.uniform(0.0, 2.0 * np.pi)
        st = np.sin(theta)

        # Compute the intersection with the detector plane at z=0
        x_det = x_flat - Z_GEN * (st / ct) * np.cos(phi)
        y_det = y_flat - Z_GEN * (st / ct) * np.sin(phi)

        # Only keep muons that hit the detector area
        if -L_SC/2 <= x_det <= L_SC/2 and -A_SC/2 <= y_det <= A_SC/2:
            E = sample_gaisser_energy(theta, rng)
            t_arrival = rng.uniform(0, T_MEAS)
            
            # Store the spatial coords at the Z_GEN plane
            generated.append({'x': x_flat, 'y': y_flat, 'ct': ct, 'st': st,
                              'phi': phi, 'E': E, 't': t_arrival})
            
    return generated

def track_muon(mu, rng):
    direction = np.array([mu['st'] * np.cos(mu['phi']),
                          mu['st'] * np.sin(mu['phi']),
                          -mu['ct']])
    origin = np.array([mu['x'], mu['y'], Z_GEN])
    deposits = []
    
    for bar_id in ('top', 'bottom'):
        bar = BARS[bar_id]
        hit = ray_box_intersection(origin, direction, bar)
        if hit is None:
            continue
        t_enter, t_exit = hit
        path = t_exit - t_enter
        if path <= 0:
            continue
        E_dep  = sample_landau_energy_loss(path, rng)
        z_mid  = 0.5 * (bar['min'][2] + bar['max'][2])
        t_mid  = (z_mid - origin[2]) / direction[2]
        x_hit  = origin[0] + t_mid * direction[0]
        deposits.append((bar_id, E_dep, x_hit, 0.0))
    return deposits

# ============================================================
# Gamma generation / tracking
# ============================================================
def generate_gammas(n_target, rng):
    """
    Generates isotropic gammas from a sphere around the detector.
    Filter to keep only those that geometrically hit the detector.
    """
    generated = []
    
    # Calculate probability of a gamma hitting the detector from a sphere
    # Roughly Area_det / (4 * pi * R^2) where R is the sphere radius
    radius = MC_LENGTH 
    p_hit = (L_SC * A_SC) / (np.pi * radius**2) # approx for top face
    
    # Generate more gammas to account for the ones that miss
    n_generate_total = int(n_target / p_hit * 1.5)
    
    for _ in range(n_generate_total):
        # Sample energy
        E = sample_power_law(1, rng, GAMMA_ALPHA, GAMMA_EMIN, GAMMA_EMAX)[0]
        
        # Sample direction isotropically
        ct_dir = rng.uniform(-1.0, 1.0)
        st_dir = np.sqrt(1.0 - ct_dir**2)
        phi_dir = rng.uniform(0.0, 2.0 * np.pi)
        dirn = np.array([st_dir * np.cos(phi_dir), st_dir * np.sin(phi_dir), ct_dir])
        
        # Place source on a sphere of radius MC_LENGTH surrounding detector center
        center = np.array([0.0, 0.0, W_SC])
        pos = center + radius * dirn
        
        # Check if it hits the detector (we can do a quick ray-trace)
        hit_bottom = ray_box_intersection(pos, -dirn, BARS['bottom'])
        hit_top    = ray_box_intersection(pos, -dirn, BARS['top'])
        
        if hit_bottom or hit_top:
            t_arrival = rng.uniform(0, T_MEAS)
            generated.append({'pos': pos, 'dirn': -dirn, 'E': E, 't': t_arrival})
            
            if len(generated) >= n_target:
                break
                
    return generated

def track_gamma(g, rng, max_scatter=8):
    pos = g['pos'].copy()
    dirn = g['dirn'].copy()
    E = g['E']
    deposits = []
    t_offset = 0.0

    for _ in range(max_scatter):
        # Find the closest bar along the current direction
        best = None
        best_t_enter = np.inf
        for bar_id, bar in BARS.items():
            hit = ray_box_intersection(pos, dirn, bar)
            if hit is None:
                continue
            if hit[0] < best_t_enter:
                best_t_enter, best_exit = hit
                best = bar_id
        if best is None:
            break

        bar  = BARS[best]
        path = best_exit - best_t_enter
        mu   = mu_compton(E)
        p_int = 1.0 - np.exp(-mu * path)

        if rng.random() > p_int:
            pos = pos + (best_exit + 0.01) * dirn
            continue

        u = rng.random()
        d_int = -np.log(1.0 - u * (1.0 - np.exp(-mu * path))) / mu
        ipos = pos + (best_t_enter + d_int) * dirn

        theta = sample_kn_theta(E, rng)
        E_prime = scattered_energy(E, theta)
        E_dep   = E - E_prime
        
        if E_dep > 0.01: # Only record if above some noise floor
            deposits.append((best, E_dep, ipos[0], t_offset))

        if E_prime < 0.05:
            break

        phi = rng.uniform(0.0, 2.0 * np.pi)
        dirn = rotate_direction(dirn, theta, phi)
        pos  = ipos + 0.01 * dirn
        E    = E_prime

    return deposits

# ============================================================
# SiPM signal from an energy deposit
# ============================================================
def deposit_to_hits(bar_id, E_dep, x_hit, event_type, event_id, t_event, rng):
    n_total = E_dep * EFF_YIELD
    hits = []
    for i, x_sipm in enumerate(SIPMS[bar_id]):
        dist = abs(x_hit - x_sipm)
        mean_ph = n_total * np.exp(-dist / LAMBDA_ATT)
        n_ph = rng.poisson(mean_ph) if mean_ph > 0 else 0
        t_light = dist / LIGHT_SPEED
        t_hit = t_event + t_light + rng.normal(0.0, TIME_JITTER)
        if bar_id == 'bottom':
            sipm_id = 'bottom_left' if i == 0 else 'bottom_right'
        else:
            sipm_id = 'top'
        hits.append({'sipm': sipm_id, 'bar': bar_id, 'photons': n_ph,
                     'time': t_hit, 'event_type': event_type,
                     'event_id': event_id})
    return hits

# ============================================================
# Coincidence finding
# ============================================================
def find_coincidences(hits, threshold=THRESHOLD, window=COIN_WINDOW):
    # 1. Filter out noise below the threshold
    valid = [h for h in hits if h['photons'] >= threshold]
    
    # 2. Sort by time
    valid.sort(key=lambda h: h['time'])

    groups = []
    if not valid:
        return groups

    current_group = [valid[0]]

    for h in valid[1:]:
        # Check the time difference against the LAST hit added to the group
        # This creates a "chain" of hits as long as no gap is > 15ns
        if abs(h['time'] - current_group[-1]['time']) <= window:
            current_group.append(h)
        else:
            # The gap is too big. Save the group and start a new one.
            if len(current_group) >= 2:
                groups.append(current_group)
            current_group = [h]

    # Don't forget to append the very last group
    if len(current_group) >= 2:
        groups.append(current_group)

    return groups

def classify(group):
    mu_events    = {h['event_id'] for h in group if h['event_type'] == 'muon'}
    gamma_events = {h['event_id'] for h in group if h['event_type'] == 'gamma'}
    return len(mu_events), len(gamma_events)

# ============================================================
# Main
# ============================================================
def main(seed=42):
    rng = np.random.default_rng(seed)
    print("=" * 60)
    print(" Gamma + Muon background simulation")
    print("=" * 60)

    # Calculate how many actually hit the detector in 1s
    n_muon  = int(MUON_FLUX  * DET_AREA * T_MEAS)
    n_gamma = int(GAMMA_FLUX * DET_AREA * T_MEAS)
    
    print(f" Target muons on detector: {n_muon}")
    print(f" Target gammas on detector: {n_gamma}")

    muons  = generate_muons(n_muon, rng)
    gammas = generate_gammas(n_gamma, rng)
    
    print(f" Successfully generated {len(muons)} muons that hit.")
    print(f" Successfully generated {len(gammas)} gammas that hit.")

    all_hits = []
    for ev_id, mu in enumerate(muons):
        for bar_id, E_dep, x_hit, t_off in track_muon(mu, rng):
            all_hits.extend(deposit_to_hits(bar_id, E_dep, x_hit, 'muon', ev_id, mu['t'] + t_off, rng))
            
    for ev_id, g in enumerate(gammas):
        for bar_id, E_dep, x_hit, t_off in track_gamma(g, rng):
            all_hits.extend(deposit_to_hits(bar_id, E_dep, x_hit, 'gamma', ev_id, g['t'] + t_off, rng))

    coincidences = find_coincidences(all_hits)

    muon_muon = muon_gamma = gamma_gamma = genuine = 0 #genuine = 1 muon or 1 gamma, muon_muon = 2 muons, muon_gamma = 1 muon + 1 gamma, gamma_gamma = 2 gammas
    coin_charges = []
    for grp in coincidences:
        nm, ng = classify(grp)
        if   nm == 1 and ng == 0: genuine    += 1
        elif nm == 0 and ng == 1: genuine    += 1
        elif nm >= 2:             muon_muon  += 1
        elif nm == 1 and ng >= 1: muon_gamma += 1
        elif ng >= 2:             gamma_gamma+= 1
        coin_charges.append(sum(h['photons'] for h in grp) / EFF_YIELD)

    print("\n--- Rates (1 s measurement) ---")
    print(f" Total coincidences      : {len(coincidences):6.2f} Hz")
    print(f"   genuine (1 event)     : {genuine:6.2f} Hz")
    print(f"   muon-muon accidental  : {muon_muon:6.2f} Hz")
    print(f"   muon-gamma accidental : {muon_gamma:6.2f} Hz")
    print(f"   gamma-gamma accidental: {gamma_gamma:6.2f} Hz")

    # ---- Plots ----
    single_ph = [h['photons'] for h in all_hits if h['photons'] > 0]

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))

    axes[0].hist(single_ph, bins=100, range=(0, 4000), histtype='step', lw=1.5, density=True)
    axes[0].set_xlabel("photoelectrons / SiPM")
    axes[0].set_ylabel("frequency")
    axes[0].set_title("Single-SiPM charge")
    axes[0].grid(True, alpha=0.3)

    if coin_charges:
        axes[1].hist(coin_charges, bins=100, histtype='step', lw=1.5, density=True)
        axes[1].set_xlabel("total deposited energy per coincidence (MeV)")
        axes[1].set_ylabel("frequency")
        axes[1].set_title("Coincidence amplitude")
        axes[1].grid(True, alpha=0.3)
    else:
        axes[1].text(0.5, 0.5, "no coincidences", ha='center')

    labels = ['genuine\n1-event', 'μ-μ', 'μ-γ', 'γ-γ']
    values = [genuine, muon_muon, muon_gamma, gamma_gamma]
    axes[2].bar(labels, values, color=['C0', 'C1', 'C2', 'C3'])
    axes[2].set_ylabel("rate (Hz)")
    axes[2].set_title("Coincidence rate breakdown")
    axes[2].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()