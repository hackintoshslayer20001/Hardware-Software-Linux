import os
import subprocess

class LaptopHardwareAPI:
    def __init__(self):
        # ---------------------------------------------------------
        # Internal Hardware Control Path Mapping
        # ---------------------------------------------------------
        self.TURBO_PATH = "/sys/devices/system/cpu/intel_pstate/no_turbo"
        self.GOVERNOR_PATH_TEMPLATE = "/sys/devices/system/cpu/cpu{}/cpufreq/scaling_governor"
        self.CPU_FREQ_PATH_TEMPLATE = "/sys/devices/system/cpu/cpu{}/cpufreq/scaling_cur_freq"
        
        self.BAT_CAPACITY = "/sys/class/power_supply/BAT0/capacity"
        self.BAT_STATUS = "/sys/class/power_supply/BAT0/status"

        self.CPU_MAX_CLOCK_MHZ = 4600 
        self.CPU_MIN_CLOCK_MHZ = 800
        self.GPU_MAX_VRAM_MB = 2048

        self._cached_coretemp_hwmon = None
        self._cached_dellsmm_hwmon = None
        self._cached_disksensor_hwmon = None

    # =============================================================
    # TAB 1 SENSORS: CPU INTERACTION HOOKS
    # =============================================================

    def get_cpu_temperature(self) -> int:
        try:
            if self._cached_coretemp_hwmon is not None:
                if os.path.exists(self._cached_coretemp_hwmon):
                    with open(self._cached_coretemp_hwmon, "r") as f:
                        return int(f.read().strip()) // 1000
                else:
                    self._cached_coretemp_hwmon = None

            for i in range(12):
                name_path = f"/sys/class/hwmon/hwmon{i}/name"
                if os.path.exists(name_path):
                    with open(name_path, "r") as f:
                        if f.read().strip() == "coretemp":
                            temp_path = f"/sys/class/hwmon/hwmon{i}/temp1_input"
                            if os.path.exists(temp_path):
                                self._cached_coretemp_hwmon = temp_path
                                with open(temp_path, "r") as f:
                                    return int(f.read().strip()) // 1000

            if os.path.exists("/sys/class/thermal/thermal_zone1/temp"):
                with open("/sys/class/thermal/thermal_zone1/temp", "r") as f:
                    return int(f.read().strip()) // 1000
            return 35
        except Exception:
            return 35

    def get_cpu_frequency(self) -> int:
        try:
            path = self.CPU_FREQ_PATH_TEMPLATE.format(0)
            if os.path.exists(path):
                with open(path, "r") as f:
                    return int(f.read().strip()) // 1000
            return 800
        except Exception:
            return 800

    def get_cpu_clock_percentage(self) -> int:
        current_freq = self.get_cpu_frequency()
        if current_freq <= 0:
            return 0
        percentage = int((current_freq / self.CPU_MAX_CLOCK_MHZ) * 100)
        return max(0, min(100, percentage))

    def get_current_governor(self) -> str:
        try:
            path = self.GOVERNOR_PATH_TEMPLATE.format(0)
            if os.path.exists(path):
                with open(path, "r") as f:
                    return f.read().strip()
            return "powersave"
        except Exception:
            return "powersave"

    def is_turbo_enabled(self) -> bool:
        try:
            if os.path.exists(self.TURBO_PATH):
                with open(self.TURBO_PATH, "r") as f:
                    return f.read().strip() == "0"
            return True
        except Exception:
            return True

    # =============================================================
    # TAB 2 SENSORS: NVIDIA HYBRID GPU ISOLATION
    # =============================================================

    def get_gpu_telemetry(self) -> dict:
        data = {"temp": 0, "utilization": 0, "vram_used": 0, "vram_total": self.GPU_MAX_VRAM_MB, "status": "Offline"}
        try:
            query = "temperature.gpu,utilization.gpu,memory.used,memory.total"
            res = subprocess.check_output(
                ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"],
                stderr=subprocess.DEVNULL,
                timeout=0.3
            )
            parsed = res.decode("utf-8").strip().split(", ")
            if len(parsed) >= 4:
                data["temp"] = int(parsed)
                data["utilization"] = int(parsed)
                data["vram_used"] = int(parsed)
                data["vram_total"] = int(parsed)
                data["status"] = "Active"
            return data
        except subprocess.TimeoutExpired:
            data["status"] = "Suspended / Sleep Mode"
            return data
        except Exception:
            data["status"] = "Idle / Standby"
            return data
    # =========================================================================
    # TAB 3 HOOKS: COOLING, MEMORY & EXPANDED OPTION C TELEMETRY
    # =========================================================================

    def get_dell_fan_speed(self) -> int:
        """Reads fan speed metrics directly from native hwmon sysfs directories."""
        try:
            if self._cached_dellsmm_hwmon is not None:
                if os.path.exists(self._cached_dellsmm_hwmon):
                    with open(self._cached_dellsmm_hwmon, "r") as f:
                        return int(f.read().strip())
                else:
                    self._cached_dellsmm_hwmon = None

            for i in range(12):
                name_path = f"/sys/class/hwmon/hwmon{i}/name"
                if os.path.exists(name_path):
                    with open(name_path, "r") as f:
                        if f.read().strip() in ["dell_smm", "i8k"]:
                            fan_path = f"/sys/class/hwmon/hwmon{i}/fan1_input"
                            if os.path.exists(fan_path):
                                self._cached_dellsmm_hwmon = fan_path
                                with open(fan_path, "r") as f:
                                    return int(f.read().strip())
            return 0
        except Exception:
            return 0

    def get_ram_utilization(self) -> dict:
        """Parses virtual memory mapping flags to calculate active RAM allocation details."""
        data = {"used_gb": 0.0, "total_gb": 16.0, "percentage": 0}
        try:
            if os.path.exists("/proc/meminfo"):
                mem = {}
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        parts = line.split(":")
                        if len(parts) == 2:
                            mem[parts[0].strip()] = int(parts[1].replace("kB", "").strip())
                
                total_kb = mem.get("MemTotal", 16000000)
                available_kb = mem.get("MemAvailable", total_kb)
                used_kb = total_kb - available_kb
                
                data["total_gb"] = round(total_kb / (1024 * 1024), 1)
                data["used_gb"] = round(used_kb / (1024 * 1024), 1)
                data["percentage"] = int((used_kb / total_kb) * 100)
            return data
        except Exception:
            return data

    def get_storage_temperature(self) -> int:
        """Scans NVMe kernel controller nodes to return physical drive metrics."""
        try:
            if self._cached_disksensor_hwmon is not None:
                if os.path.exists(self._cached_disksensor_hwmon):
                    with open(self._cached_disksensor_hwmon, "r") as f:
                        return int(f.read().strip()) // 1000
                else:
                    self._cached_disksensor_hwmon = None

            for i in range(12):
                name_path = f"/sys/class/hwmon/hwmon{i}/name"
                if os.path.exists(name_path):
                    with open(name_path, "r") as f:
                        if "nvme" in f.read().strip():
                            temp_path = f"/sys/class/hwmon/hwmon{i}/temp1_input"
                            if os.path.exists(temp_path):
                                self._cached_disksensor_hwmon = temp_path
                                with open(temp_path, "r") as f:
                                    return int(f.read().strip()) // 1000
            return 30
        except Exception:
            return 30

    def get_battery_telemetry(self) -> dict:
        data = {"percentage": 100, "status": "Unknown"}
        try:
            if os.path.exists(self.BAT_CAPACITY):
                with open(self.BAT_CAPACITY, "r") as f:
                    data["percentage"] = int(f.read().strip())
                with open(self.BAT_STATUS, "r") as f:
                    data["status"] = f.read().strip()
            return data
        except Exception:
            return data

    # =========================================================================
    # HARDWARE CONTROL WRITERS (SETTERS)
    # =========================================================================

    def set_cpu_governor(self, governor: str) -> bool:
        if governor not in ["performance", "powersave"]:
            raise ValueError("Governor must be 'performance' or 'powersave'")
        cmd = f"echo {governor} | pkexec tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
        return os.system(cmd) == 0

    def set_turbo_boost(self, enable: bool) -> bool:
        val = "0" if enable else "1"
        cmd = f"echo {val} | pkexec tee {self.TURBO_PATH}"
        return os.system(cmd) == 0


# =========================================================================
# PRODUCTION ENGINE VERIFICATION LOOP (LAB RUNNER)
# =========================================================================
if __name__ == "__main__":
    import time
    print("=============================================================")
    print("   DELL LATITUDE 5401 PRODUCTION CORE STABLE PIPELINE LAB")
    print("=============================================================\n")
    
    api = LaptopHardwareAPI()
    print("[SYSTEM] Running standalone data checks. Interrupt via Ctrl+C...\n")
    
    try:
        while True:
            gpu = api.get_gpu_telemetry()
            bat = api.get_battery_telemetry()
            ram = api.get_ram_utilization()
            
            print(f" -> CPU Package:  {api.get_cpu_temperature()}°C | Clock: {api.get_cpu_frequency()} MHz | Ring: {api.get_cpu_clock_percentage()}%")
            print(f" -> NVIDIA GPU:   State: {gpu['status']} | Core Temp: {gpu['temp']}°C | Compute: {gpu['utilization']}%")
            print(f" -> Fan & Power:  Cooling: {api.get_dell_fan_speed()} RPM | Battery: {bat['percentage']}% [{bat['status']}]")
            print(f" -> Option C:     Active RAM: {ram['used_gb']}GB / {ram['total_gb']}GB [{ram['percentage']}%] | NVMe: {api.get_storage_temperature()}°C")
            print("-" * 68)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[SYSTEM] Lab verification loops closed safely.")