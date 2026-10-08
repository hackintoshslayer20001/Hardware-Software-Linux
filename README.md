# Elite Hardware Commander 🚀 [Beta 1.1]

An elegant, modern dark-themed hardware monitoring and control center tailored specifically for the **Dell Latitude 5401** running Linux. Built with **Python 3, PyQt6, and PyQtGraph**, this utility ditches the clunky interfaces of vintage Linux tools for a sleek, responsive tabbed dashboard ecosystem.

---

## 🖼️ Interface Preview
*The application features custom-painted vector indicators, live moving historical charts, and isolated telemetry control spaces.*

---

## ✨ Active Feature Roadmap

### 📦 Beta 1.1 (Current Stable)
*   **Vector Circular Gauge Ring:** Dynamically tracks scaling percentages right inside a smooth electric blue canvas arc.
*   **True MHz Core Speed Readout:** Draws live, fluctuating clock speed metrics squarely in the center of the panel gauge.
*   **Silicon ACPI Package Fix:** True thermal tracking loops reading native internal core junctions dynamically instead of locking flat at 25°C.
*   **Anti-Glitch Sleep Shields:** Subprocess timeout rules that isolate your hybrid NVIDIA MX150, keeping your UI perfectly fluid when the card falls into energy-saving hibernation.
*   **Option C Subsystems:** A completely stacked diagnostics tab providing real-time mechanical fan speed **RPM variables**, live **battery statuses**, active **system RAM memory percentages**, and raw internal **NVMe storage drive thermals** side-by-side.

### 🔮 Upcoming Milestones
*   **Beta 1.2:** Automated Power Plan Toggles (Sensing AC charger connections/disconnections to shift profiles on auto-pilot).
*   **Beta 2.0:** Thermal Safety Guard warnings (Flashing card UI panels vibrant red and dropping desktop toast notifications on high thermal spikes).
*   **Beta 4.0:** Full Cross-Platform Port (Bypassing Linux-specific `sysfs` tracks using `psutil` wrappers to bring native support to Windows & macOS environments).

---

## 🛠️ Installation & Deployment

The quickest way to deploy Elite Hardware Commander on Ubuntu, Linux Mint, or Debian is by using our compiled `.deb` package installer.

### 1. Simple Double-Click Install
1. Head over to our [GitHub Releases Page](https://github.com).
2. Download the latest `hardware-commander_1.0_amd64.deb` file artifact.
3. Open your file manager, double-click the downloaded `.deb` file, and click **Install** via your system Software Center app.

### 2. Terminal Alternative Installation
If you prefer using the command line shell, install the compiled package directly via `apt`:
```bash
sudo apt update
sudo apt install ./hardware-commander_1.0_amd64.deb
```

---

## 🚀 Running the App
Once installed, close your terminal. Press your keyboard's **Super key** (the Ubuntu/Windows key), type **"Elite Hardware Commander"**, and hit enter. 

You can right-click its app tile on your system panel sidebar tray dock and select **"Add to Favorites"** to keep it pinned permanently right next to your default system browser!

---

## 📄 License
This system utility utility dashboard is open-source software distributed under the terms of the MIT License.
