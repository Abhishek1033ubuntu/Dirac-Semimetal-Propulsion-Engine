import numpy as np
import matplotlib.pyplot as plt

class BrachistochroneTrajectorySolver:
    """
    Solves continuous-acceleration propellantless transit trajectories (m(t) = m_0)
    for Space-Borne Transport craft operating under continuous PMC-boosted thrust.
    """
    def __init__(self, craft_mass_kg=2500.0, net_thrust_kN=24.88):
        self.craft_mass_kg = craft_mass_kg
        self.net_thrust_N = net_thrust_kN * 1000.0
        self.acceleration = self.net_thrust_N / self.craft_mass_kg  # m/s^2 (~9.95 m/s^2)
        self.g_force = self.acceleration / 9.81

        # Standard Space Missions (Distances in meters)
        self.missions = {
            'LEO to GEO Transfer': 35.386e6,      # 35,386 km orbital delta
            'Earth-Moon Transit': 384.4e6,        # 384,400 km lunar distance
            'Earth-Mars Transit (Closest)': 54.6e9 # 54.6 million km
        }

    def solve_mission_transit(self, distance_m):
        """
        Calculates 50% flip-point brachistochrone transit metrics.
        Continuous acceleration to midpoint -> 180 deg turnover -> continuous deceleration.
        """
        d_flip = distance_m / 2.0
        t_flip_sec = np.sqrt(2.0 * d_flip / self.acceleration)
        t_total_sec = 2.0 * t_flip_sec
        v_peak_m_s = self.acceleration * t_flip_sec
        
        return {
            'transit_time_sec': t_total_sec,
            'transit_time_hours': t_total_sec / 3600.0,
            'transit_time_days': t_total_sec / 86400.0,
            'v_peak_km_s': v_peak_m_s / 1000.0,
            'd_flip_km': d_flip / 1000.0
        }

    def generate_trajectory_profile(self, distance_m, num_points=1000):
        """Generates time-series arrays for position, velocity, and acceleration."""
        res = self.solve_mission_transit(distance_m)
        t_total = res['transit_time_sec']
        t_flip = t_total / 2.0
        
        t_array = np.linspace(0, t_total, num_points)
        v_array = np.zeros_like(t_array)
        x_array = np.zeros_like(t_array)
        a_array = np.zeros_like(t_array)
        
        for i, t in enumerate(t_array):
            if t <= t_flip:
                a_array[i] = self.acceleration
                v_array[i] = self.acceleration * t
                x_array[i] = 0.5 * self.acceleration * t**2
            else:
                a_array[i] = -self.acceleration
                dt = t - t_flip
                v_array[i] = res['v_peak_km_s'] * 1000.0 - self.acceleration * dt
                x_array[i] = (distance_m / 2.0) + (res['v_peak_km_s'] * 1000.0 * dt) - (0.5 * self.acceleration * dt**2)
                
        return t_array, x_array / 1000.0, v_array / 1000.0, a_array

if __name__ == "__main__":
    solver = BrachistochroneTrajectorySolver(craft_mass_kg=2500.0, net_thrust_kN=24.88)
    
    print("=========================================================")
    print("  PHASE 3: PROPELLANTLESS BRACHISTOCHRONAL TRANSIT SOLVER")
    print("=========================================================")
    print(f"Craft Wet/Dry Mass (m = m0) : {solver.craft_mass_kg:.1f} kg (Zero Fuel Mass Loss)")
    print(f"Continuous Net Thrust       : {solver.net_thrust_N / 1000.0:.2f} kN")
    print(f"Continuous Acceleration     : {solver.acceleration:.2f} m/s^2 ({solver.g_force:.2f}g)")
    print("---------------------------------------------------------")
    
    for name, dist in solver.missions.items():
        m_res = solver.solve_mission_transit(dist)
        print(f"Mission: {name}")
        print(f"  Distance                 : {dist/1e6:.1f} thousand km")
        if m_res['transit_time_hours'] < 48.0:
            print(f"  Total Transit Duration   : {m_res['transit_time_hours']:.2f} Hours ({m_res['transit_time_sec']/60.0:.1f} mins)")
        else:
            print(f"  Total Transit Duration   : {m_res['transit_time_days']:.2f} Days ({m_res['transit_time_hours']:.1f} hours)")
        print(f"  Peak Midpoint Velocity   : {m_res['v_peak_km_s']:.2f} km/s")
        print("---------------------------------------------------------")

    # Plot Earth-Moon Brachistochrone Trajectory Profile
    t_arr, x_arr, v_arr, a_arr = solver.generate_trajectory_profile(solver.missions['Earth-Moon Transit'])
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    ax1.plot(t_arr / 3600.0, v_arr, color='teal', lw=2.5, label='Velocity Profile (km/s)')
    ax1.axvline(t_arr[-1]/7200.0, color='crimson', linestyle='--', label=r'180° Turnover / Deceleration Flip')
    ax1.set_ylabel('Velocity (km/s)', fontweight='bold')
    ax1.set_title('Earth-Moon 1.01g Constant-Acceleration Transit Profile', fontweight='bold')
    ax1.grid(True, ls="--", alpha=0.5)
    ax1.legend()
    
    ax2.plot(t_arr / 3600.0, x_arr / 1000.0, color='darkorange', lw=2.5, label='Distance Profile (Thousand km)')
    ax2.axvline(t_arr[-1]/7200.0, color='crimson', linestyle='--')
    ax2.set_xlabel('Elapsed Time (Hours)', fontweight='bold')
    ax2.set_ylabel('Distance (10³ km)', fontweight='bold')
    ax2.grid(True, ls="--", alpha=0.5)
    ax2.legend()
    
    plt.tight_layout()
    plt.show()
