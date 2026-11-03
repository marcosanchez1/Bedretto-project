"""
Gamma background estimation using
Compton scattering and Klein-Nishina cross sections.

I Just translated Federico's program to python and tried to understand it.
I did change the assumption of doing a uniform sampling on the scattered photon.
"""

import numpy as np
import matplotlib.pyplot as plt

# ==========================================================
# Constants
# ==========================================================

MEC2 = 0.510998950      # mass of electron at rest in MeV
R0 = 2.8179403262e-13  # classical radius of electron in cm
SIGMA_T = 0.665245873e-24 # Thomson cross section cm^-2
NA = 6.02214076e23 # Avogadro's number

# ==========================================================
# Compton kinematics
# ==========================================================

def scattered_energy(E0, theta):
    x = E0 / MEC2
    return E0 / (1.0 + x * (1.0 - np.cos(theta))) # Energy of outgoing photon after Compton when scatterd at a certain angle.

# ==========================================================
# Klein-Nishina
# ==========================================================

def dSigmaKN_dOmega(E0, theta):
    Ep = scattered_energy(E0, theta)
    ratio = Ep / E0
    s2 = np.sin(theta)**2
    return (0.5 * R0**2 * ratio**2 * (ratio + 1.0 / ratio - s2))

def sigmaKN_total(E0):
    x = E0 / MEC2
    l = np.log(1.0 + 2.0 * x)

    term1 = (((1.0 + x) / x**2) * (2.0 * (1.0 + x) / (1.0 + 2.0 * x) - l / x))
    term2 = l / (2.0 * x)
    term3 = ((1.0 + 3.0 * x) / (1.0 + 2.0 * x)**2)

    return (2.0 * np.pi * R0**2 * (term1 + term2 - term3))

#Sampling using the pdf
def sample_kn_energy(E0, rng):
    accept = False
    while accept == False:
        ct = rng.uniform(-1, 1)
        theta = np.arccos(ct)
        dsig = dSigmaKN_dOmega(E0, theta)
        max_dsig = dSigmaKN_dOmega(E0, 0.0)          # forward peak
        accept = rng.uniform(0, max_dsig) < dsig
    return scattered_energy(E0, theta)

# ==========================================================
# Interaction probability
# ==========================================================

def mu_compton(E0,ED):
    return ED * sigmaKN_total(E0)


def p_interaction(E0, L, ED):
    return (1.0 - np.exp(-mu_compton(E0, ED) * L))

# ==========================================================
# Main simulation
# ==========================================================

def main():

    # ------------------------------
    # Material properties
    # ------------------------------

    ED_EJ200 = 3.33e23 # the data sheet gives us directly the electron density(e*cm^-3)
    W_SC = 1.0 # Width of scintillators
    L_SC = 169.0
    A_SC = 6.0

    ED_AL = 1.81e23 #And we can get also the electron density directly for aluminum
    W_AL = 0.0 # Width of aluminum bewteen scintillators(in reality we have none)
    L_AL = 169.0
    A_AL = 6.0
    

    # ------------------------------
    # Example at 200 keV
    # ------------------------------
    E0 = 0.2

    print(f"\n=== {E0:.3f} MeV gamma in 1 cm PMMA ===")
    print(f"sigma_KN total = {sigmaKN_total(E0)*1e24:.4f} barn")
    print(f"mu_C = {mu_compton(E0,ED_EJ200):.4f} cm^-1")
    print(f"P_int (1 cm) = {100*p_interaction(E0,1,ED_EJ200):.3f} %")
    print(f"E' at 90° = {scattered_energy(E0,np.pi/2):.4f} MeV")
    print(f"Compton edge = {scattered_energy(E0, np.pi):.4f} MeV")
    print(f"\ndSigma/dOmega at 90° = {dSigmaKN_dOmega(E0,np.pi/2):.4e} cm²/sr")

    # ======================================================
    # Simulation: Scan 150 keV -> 3.5 MeV
    # ======================================================

    nbins = 100

    energies = np.linspace(0.15, 3.5, nbins) #
    probabilities = np.zeros(nbins)

    rng = np.random.default_rng() #Random number generator

    N_MC = 10000 # Number of Montecarlos

    for i, E0 in enumerate(energies):

        P1 = p_interaction(E0, W_SC, ED_EJ200) # probability that an incident photon with energy E0 interacts with the first scintillator.
        
        PE_MIN = scattered_energy(E0, np.pi) # min. value of the energy of the scattered photon.
        PROBABILITY = 0
        for _ in range(N_MC):
            E1 = sample_kn_energy(E0, rng) #with this we use the klein-nishina pdf to sample instead of assuming is uniform.

            # Probability that gamma traverses the aluminium without interacting AND interacts on the second scintillator
            v = ((1.0 - p_interaction(E1, W_AL, ED_AL)) * p_interaction(E1, W_SC, ED_EJ200))
            PROBABILITY += v
        
        # Average over all MCs to get the probability it survives and interacts also on
        # the first scintillator and multiply by 100 to get the percent.
        probabilities[i] = 100 * P1 * (PROBABILITY / N_MC)

    # ======================================================
    # Plot
    # ======================================================

    plt.figure(figsize=(8,5))

    plt.plot(energies, probabilities, lw=2)

    plt.xlabel("Gamma energy (MeV)")
    plt.ylabel("Double-hit probability (%)")

    plt.title("Probability that a gamma produces\nsignals in both scintillators")

    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()