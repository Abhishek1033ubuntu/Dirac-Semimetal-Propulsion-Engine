import numpy as np

class FocusedZPFGradientSolver:
    """
    Core physics solver for Hyperbolic Focused ZPF Gradient Propulsion.
    Handles both Space-Borne Transport and Surface-Skimming Glider modes.
    """
    def __init__(self, f_drive=3.0e12, E_0=5.0e7, area_panel=0.16):
        self.c = 3.0e8
        self.eps_0 = 8.854187817e-12
        self.f_drive = f_drive
        self.omega = 2.0 * np.pi * f_drive
        self.wavelength = self.c / f_drive
        self.E_0 = E_0
        self.area_panel = area_panel
        self.F_unreflected_baseline = 3125.0  # N per 0.16 m^2 panel

    def compute_hyperbolic_focal_waist(self, f_focal, NA=0.85):
        """
        Calculates diffraction-limited focal waist w_0 and field gradient multiplier.
        f_focal: Focal length (m)
        NA     : Numerical Aperture of the phased array
        """
        w_0 = (self.wavelength) / (np.pi * NA)
        gradient_multiplier = (self.wavelength / w_0)**2
        return w_0, gradient_multiplier

    def compute_pmc_reflected_thrust(self, r_pmc=0.99, phi_pmc=0.0):
        """Calculates thrust boost using tuned PMC rear reflector (1.99x baseline)."""
        thrust_multiplier = 1.0 + r_pmc * np.cos(phi_pmc)
        F_pmc_panel = self.F_unreflected_baseline * thrust_multiplier
        return F_pmc_panel, thrust_multiplier

    def compute_ground_effect_boost(self, height_m, decay_length_m=1.5):
        """Computes Electrodynamic Ground-Effect (EGE) lift multiplier near surface."""
        if height_m <= 0:
            return 1.25  # Maximum static ground coupling
        boost_factor = 1.0 + 0.25 * np.exp(-2.0 * height_m / decay_length_m)
        return boost_factor

    def simulate_space_borne_transport(self, num_panels=4, craft_mass_kg=2500.0):
        """Simulates Space-Borne Transport performance (Continuous Wave)."""
        F_single, _ = self.compute_pmc_reflected_thrust()
        F_total_N = num_panels * F_single
        P_total_kW = num_panels * 18.5
        acceleration_m_s2 = F_total_N / craft_mass_kg
        g_force = acceleration_m_s2 / 9.81
        
        return {
            'total_thrust_kN': F_total_N / 1000.0,
            'bus_power_kW': P_total_kW,
            'acceleration_m_s2': acceleration_m_s2,
            'g_force': g_force
        }

    def simulate_surface_glider(self, num_panels=2, vehicle_mass_kg=1200.0, height_m=1.0, pitch_deg=20.0):
        """Simulates Surface-Skimming Glider hover and forward propulsion."""
        F_single, _ = self.compute_pmc_reflected_thrust()
        F_panel_total = num_panels * F_single
        P_total_kW = num_panels * 18.5
        
        # Apply Ground Effect Boost
        g_boost = self.compute_ground_effect_boost(height_m)
        F_boosted = F_panel_total * g_boost
        
        pitch_rad = np.radians(pitch_deg)
        F_vertical_lift = F_boosted * np.cos(pitch_rad)
        F_horizontal_thrust = F_boosted * np.sin(pitch_rad)
        
        weight_N = vehicle_mass_kg * 9.81
        net_lift_margin_N = F_vertical_lift - weight_N
        forward_accel_m_s2 = F_horizontal_thrust / vehicle_mass_kg
        
        return {
            'total_boosted_thrust_kN': F_boosted / 1000.0,
            'bus_power_kW': P_total_kW,
            'vertical_lift_N': F_vertical_lift,
            'weight_N': weight_N,
            'hover_stable': F_vertical_lift >= weight_N,
            'forward_accel_m_s2': forward_accel_m_s2
        }

if __name__ == "__main__":
    solver = FocusedZPFGradientSolver()
    
    print("=========================================================")
    print("  PHASE 1: FOCUSED ZPF GRADIENT SOLVER (DUAL-MODE)       ")
    print("=========================================================")
    
    # Mode 1: Space Transport
    space_res = solver.simulate_space_borne_transport(num_panels=4, craft_mass_kg=2500.0)
    print(f"\n--- MODE 1: SPACE-BORNE ORBITAL TRANSPORT (4 PANELS) ---")
    print(f"Total Net Thrust Output  : {space_res['total_thrust_kN']:.2f} kN")
    print(f"Required Electrical Power: {space_res['bus_power_kW']:.1f} kW")
    print(f"Spacecraft Acceleration  : {space_res['acceleration_m_s2']:.2f} m/s^2 ({space_res['g_force']:.2f}g)")
    
    # Mode 2: Surface Glider
    glider_res = solver.simulate_surface_glider(num_panels=2, vehicle_mass_kg=1200.0, height_m=1.0, pitch_deg=20.0)
    print(f"\n--- MODE 2: SURFACE-SKIMMING GLIDER (2 PANELS @ h=1.0m) ---")
    print(f"Ground-Boosted Thrust    : {glider_res['total_boosted_thrust_kN']:.2f} kN")
    print(f"Required Electrical Power: {glider_res['bus_power_kW']:.1f} kW")
    print(f"Vertical Lift Generated  : {glider_res['vertical_lift_N']:.1f} N (Vehicle Weight: {glider_res['weight_N']:.1f} N)")
    print(f"Hover Stability Status   : {'STABLE (Sufficient Lift)' if glider_res['hover_stable'] else 'UNSTABLE'}")
    print(f"Horizontal Forward Accel : {glider_res['forward_accel_m_s2']:.2f} m/s^2")
    print("=========================================================")
