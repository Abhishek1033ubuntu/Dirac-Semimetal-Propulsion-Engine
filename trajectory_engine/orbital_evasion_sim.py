import numpy as np

class OrbitalEvasionAndDebrisSolver:
    """
    Solves high-G pulsed burst evasion mechanics, electronic vector inversion,
    and hyper-velocity electrodynamic debris deflection for space-borne transports.
    """
    def __init__(self, craft_mass_kg=2500.0, num_panels=4, CW_panel_thrust_kN=6.2188):
        self.craft_mass_kg = craft_mass_kg
        self.num_panels = num_panels
        self.CW_panel_thrust_N = CW_panel_thrust_kN * 1000.0
        
        # Continuous Wave (CW) Baseline Force across array
        self.F_CW_total_N = self.num_panels * self.CW_panel_thrust_N
        self.a_CW_m_s2 = self.F_CW_total_N / self.craft_mass_kg
        
        # Pulsed Compression Parameters (10x Field Strength -> 100x Peak Force at 1% Duty Cycle)
        self.pulse_field_boost = 10.0
        self.duty_cycle = 0.01  # 1% Duty Cycle
        self.F_peak_pulse_N = self.F_CW_total_N * (self.pulse_field_boost**2)  # 100x force during pulse
        self.a_peak_pulse_m_s2 = self.F_peak_pulse_N / self.craft_mass_kg
        self.g_peak_pulse = self.a_peak_pulse_m_s2 / 9.81

    def solve_pulsed_evasion_maneuver(self, pulse_duration_ms=50.0):
        """
        Calculates instantaneous velocity shift (delta-V) and displacement 
        achieved during a high-G pulse burst maneuver.
        """
        t_pulse_sec = pulse_duration_ms / 1000.0
        delta_v_m_s = self.a_peak_pulse_m_s2 * t_pulse_sec
        displacement_m = 0.5 * self.a_peak_pulse_m_s2 * (t_pulse_sec**2)
        
        # Average power draw remains identical to CW mode due to 1% duty cycle
        P_avg_kW = self.num_panels * 18.5
        
        return {
            'peak_thrust_MN': self.F_peak_pulse_N / 1e6,
            'peak_acceleration_g': self.g_peak_pulse,
            'pulse_duration_ms': pulse_duration_ms,
            'delta_v_m_s': delta_v_m_s,
            'evasion_displacement_m': displacement_m,
            'avg_power_draw_kW': P_avg_kW
        }

    def solve_electronic_vector_inversion(self):
        """Calculates zero-slew phase inversion response time vs mechanical CMG turnover."""
        phase_switch_time_us = 0.45  # 450 nanoseconds electronic switching
        mechanical_slew_time_sec = 180.0  # 3 minutes for 180-deg hull rotation
        
        return {
            'electronic_switch_us': phase_switch_time_us,
            'mechanical_slew_sec': mechanical_slew_time_sec,
            'time_savings_factor': (mechanical_slew_time_sec * 1e6) / phase_switch_time_us
        }

    def simulate_debris_deflection(self, particle_mass_g=0.01, relative_velocity_km_s=737.0, interaction_dist_m=10.0):
        """
        Calculates lateral trajectory offset imparted on incoming micro-meteoroid debris
        by the THz electrodynamic fringe-field deflection zone.
        """
        v_rel_m_s = relative_velocity_km_s * 1000.0
        m_particle_kg = particle_mass_g / 1000.0
        
        # Interaction duration inside the 10 m deflection zone
        t_impact_sec = interaction_dist_m / v_rel_m_s
        
        # Electrodynamic deflection force exerted on ionized debris grain
        F_deflect_N = 85.0  # 85 N fringe force
        a_deflect_m_s2 = F_deflect_N / m_particle_kg
        
        # Lateral displacement offset away from hull skin
        lateral_offset_m = 0.5 * a_deflect_m_s2 * (t_impact_sec**2)
        safe_clearance = lateral_offset_m > 0.05  # > 5 cm clearance
        
        return {
            'relative_velocity_km_s': relative_velocity_km_s,
            'debris_mass_mg': particle_mass_g * 1000.0,
            'interaction_time_us': t_impact_sec * 1e6,
            'lateral_offset_cm': lateral_offset_m * 100.0,
            'deflection_status': 'DEFLECTED (Safe Clearance)' if safe_clearance else 'IMPACT RISK'
        }

if __name__ == "__main__":
    solver = OrbitalEvasionAndDebrisSolver(craft_mass_kg=2500.0, num_panels=4, CW_panel_thrust_kN=6.2188)
    
    print("=========================================================")
    print("  PHASE 3 (PART 2): HIGH-G EVASION & DEBRIS DEFLECTION  ")
    print("=========================================================")
    
    # 1. High-G Evasion Burst
    evasion = solver.solve_pulsed_evasion_maneuver(pulse_duration_ms=50.0)
    print(f"\n--- 1. PULSED HIGH-G EVASION BURST (50 ms PULSE) ---")
    print(f"Peak Array Thrust Output : {evasion['peak_thrust_MN']:.3f} MN ({evasion['peak_thrust_MN']*1000:.1f} kN)")
    print(f"Instantaneous Acceleration: {evasion['peak_acceleration_g']:.2f}g ({evasion['peak_acceleration_g']*9.81:.1f} m/s^2)")
    print(f"Maneuver Velocity Shift   : Delta-V = {evasion['delta_v_m_s']:.2f} m/s in 50 ms")
    print(f"Lateral Evasion Distance : {evasion['evasion_displacement_m']:.2f} meters displacement")
    print(f"Average Bus Power Draw    : {evasion['avg_power_draw_kW']:.1f} kW (1% Duty Cycle cap)")

    # 2. Electronic Vector Inversion
    inversion = solver.solve_electronic_vector_inversion()
    print(f"\n--- 2. ELECTRONIC ZERO-SLEW VECTOR INVERSION ---")
    print(f"Phase Inversion Time     : {inversion['electronic_switch_us']:.2f} microseconds (Electronic)")
    print(f"Mechanical CMG Hull Slew : {inversion['mechanical_slew_sec']:.1f} seconds")
    print(f"Turnover Speedup Gain    : {inversion['time_savings_factor']:.1e}x faster vector response")

    # 3. Debris Deflection
    debris = solver.simulate_debris_deflection(particle_mass_g=0.01, relative_velocity_km_s=737.0)
    print(f"\n--- 3. HYPER-VELOCITY DEBRIS DEFLECTION (MARS TRANSIT) ---")
    print(f"Threat Relative Speed    : {debris['relative_velocity_km_s']:.1f} km/s ({debris['relative_velocity_km_s']*1000:.0f} m/s)")
    print(f"Particle Mass / Size     : {debris['debris_mass_mg']:.1f} mg (10 mm Grain)")
    print(f"Field Interaction Time   : {debris['interaction_time_us']:.2f} microseconds")
    print(f"Deflected Clearance      : {debris['lateral_offset_cm']:.2f} cm outward shift")
    print(f"Deflection Status        : {debris['deflection_status']}")
    print("=========================================================")
