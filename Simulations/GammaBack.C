// compton.cpp -- Compton kinematics + Klein-Nishina probability in plastic
#include <cstdio>
#include <cmath>

// ---- constants ----
const double MEC2   = 0.510998950;     // m_e c^2 (MeV)
const double R0     = 2.8179403262e-13;// classical electron radius (cm)
const double SIGMA_T= 0.665245873e-24; // Thomson cross section (cm^2)
const double NA     = 6.02214076e23;   // Avogadro (1/mol)

// ---- 1. Kinematics: emerging gamma energy ----
double scatteredEnergy(double E0, double theta){
    double x = E0/MEC2;
    return E0 / (1.0 + x*(1.0 - std::cos(theta)));
}

// ---- Compton edge (max recoil-electron energy) ----
double comptonEdge(double E0){
    return E0 - E0/(1.0 + 2.0*E0/MEC2);
}

// ---- 2a. Klein-Nishina DIFFERENTIAL cross section (cm^2/sr) ----
double dSigmaKN_dOmega(double E0, double theta){
    double Ep = scatteredEnergy(E0, theta);
    double ratio = Ep/E0;
    double s2 = std::sin(theta)*std::sin(theta);
    return 0.5*R0*R0 * ratio*ratio * (ratio + 1.0/ratio - s2);
}

// ---- 2b. Klein-Nishina TOTAL cross section per electron (cm^2) ----
double sigmaKN_total(double E0){
    double x = E0/MEC2;
    double l = std::log(1.0 + 2.0*x);
    double term1 = ((1.0+x)/(x*x)) * (2.0*(1.0+x)/(1.0+2.0*x) - l/x);
    double term2 = l/(2.0*x);
    double term3 = (1.0+3.0*x)/((1.0+2.0*x)*(1.0+2.0*x));
    return 2.0*M_PI*R0*R0 * (term1 + term2 - term3);
}

// ---- 3. Linear Compton attenuation coefficient (cm^-1) ----
// ne = rho * NA * (Z/A)_eff   ; for PMMA rho=1.18, Z/A=0.408
double muCompton(double E0, double rho, double ZoverA){
    double ne = rho * NA * ZoverA;          // electrons / cm^3
    return ne * sigmaKN_total(E0);
}

// ---- Probability of >=1 Compton interaction over path L (cm) ----
double pInteraction(double E0, double L, double rho, double ZoverA){
    return 1.0 - std::exp(-muCompton(E0, rho, ZoverA) * L);
}

int GammaBack(void) {
    const double RHO_PMMA = 1.18, ZA_PMMA = 0.408;
    const double RHO_AL = 2.7,  ZA_AL = 0.482;

    double E0 = 0.2;
    
    printf("=== %f  MeV gamma in 1 cm PMMA ===\n",E0);

    printf("sigma_KN total      = %.4f barn\n", sigmaKN_total(E0)*1e24);
    printf("mu_C                = %.4f cm^-1\n", muCompton(E0,RHO_PMMA,ZA_PMMA));
    printf("P_int (1 cm)        = %.3f %%\n", 100*pInteraction(E0,1.0,RHO_PMMA,ZA_PMMA));
    printf("E' at 90 deg        = %.4f MeV\n", scatteredEnergy(E0,M_PI/2));
    printf("Compton edge        = %.4f MeV\n", comptonEdge(E0));

    printf("\n=== dSigma/dOmega at 90 deg (cm^2/sr) ===\n");
    printf("= %.4e\n", dSigmaKN_dOmega(E0,M_PI/2));

    printf("\n=== Scan 100 keV - 3.5 MeV in 1 cm PMMA ===\n");


    int nbins = 100;
    
    TH1D *h = new TH1D("h","  ",nbins,0.15,3.5); 
    
    TRandom r; 

    double W_AL = 5.;

    
    for(int i = 0; i < nbins ; i++ ) { 

      E0 = h->GetBinCenter(i+1); 
    
      double Probability = 0.; 
    
      for(int j = 0; j < 1e+5;j++ ) {
	
	double E1 = r.Uniform(0,comptonEdge(E0));  // Assume flat distribution of gammas. 

	

	
	double v = (1.-pInteraction(E1,W_AL,RHO_AL,ZA_AL))*pInteraction(E1,1.0,RHO_PMMA,ZA_PMMA);

	if( v > 0 ) 
	  Probability += v;
	else
	  j--;
	
      }

      double Val = 100*pInteraction(E0,1.0,RHO_PMMA,ZA_PMMA)*Probability/1.e+5;
      
      //   printf(" E = %f , Double hit probability %f %% \n  ",E0, Val);

      h->SetBinContent(i+1,Val); 
    
    }

    h->Draw();

    
    return 0;
}
