import lasio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap

# Dictionary mapping common log mnemonics
data_dict = {
    "ROP": ["ROP", "10FTRATE", "10FTROP", "5FTRATE", "5FTROP", "DR", "DRILLRATE", "FTPERHR", "ROP:1", "ROP:2", "ROPI", "ROPTVD"],
    "Cal": ["Cal", "CAL1", "CAL2", "CAL3", "CAL4", "CAL5", "CAL6", "CAL7", "CALD", "CALI", "CALIFLG", "CALR", "CALS", "CALX", "CALXD", "CALXR", "CALYD"],
    "GR": ["GR", "CGR", "CGRD", "ECGR", "ECGR_TMG", "GR_EDTC", "GR_TMG", "GRC", "GRCM", "GRCO", "GRCX", "GRD", "GRFET", "GRGC", "GRR", "GRS", "GRTO", "GRW", "HCGR", "HGR", "HSGR", "MWD-GR", "NATURAL_GAMMA", "SGR", "SGRDD", "GAMMA",'GR_MWD'],
    "SP": ["SP", "SPR"],
    "RHOB": ["RHOB", "ZDEN", "RHOBEDIT", "RHOL", "RHOZ"],
    "DPHI": ["DPHI", "CDL_LS", "DPDL", "DPH8", "DPHD", "DPHI_LS", "DPHIL", "DPHIVV", "DPHZ", "DPLS", "DPRL", "PORD", "PORZ", "PORZC_LS", "PRZC", "DPHS",'DNPH'],
    "NPHI": ["NPHI", "CNLS", "CNPORU", "CNS_LS", "DNPH", "HNPO", "HTNP", "NLIM", "NPDL", "NPHI_LS", "NPHL", "NPLS", "NPOR", "NPRL", "TNPH", "TNPH_LIM",'CNLS'],
    "XPHI": ["XPHI", "CPPZ", "CPZC", "PHIX", "PXND", "PXND_HILT"],
    "SPHI": ["SPHI", "SPH1", "SPHI_LS", "SPHL", "XPOR"],
    "PEF": ["PEF", "PE", "PEF8", "PEFZ"],
    "DeepRes": ["ILD", "90IN_4FT_R", "90IN_4FT_R_S", "AHT90", "AT90", "ATCO90", "RILD", "RLA5", "RO90", "DDLL", "DEEP_RESISTIVITY", "HLLD", "IDPH", "LGRD", "RD", "RESISTIVITY_(SHORT-SPACING)", "RESISTIVITY", "RESISTIVITY_(LONG-SPACING)", "RESISTIVITY_(SHORT-SPACING)", "RILD", "RLA5", "RO90", "RT90"],
    "MedRes": ["ILM", "LLM", "AHT60", "60IN_4FT_R", "IMPH", "RF60", "RILM", "RLA3", "RMLL", "RO60", "RT60",'AO30'],
    "ShalRes": ["RXO", "RXO8", "RXOZ", "RXO_HRLT", "RXRT", "SFLU", "SGRD", "SHORT_RESISTIVITY", "DSLL", "HLLS", "RLA1", "RS", "RSOZ", "RT10", "AHT10", "AT30", "RF10", "RO10"]
}

# Function to get best available log
def get_best_log(alias_group):
    """Finds the best available mnemonic for a given alias group in the LAS file."""
    for mnemonic in alias_group:
        if mnemonic in las.keys():
            log_data = las[mnemonic]
            if np.all(np.isnan(log_data)):  
                print(f"Warning: {mnemonic} found but contains only NaN values.")
                continue
            return mnemonic, log_data  
    print(f"Warning: No matching log found for {alias_group[0]}")
    return None, None  

# File paths
las_file_path = input("input desired .las file path")

# Load LAS file
las = lasio.read(las_file_path)
depth = las.index

print([curve.mnemonic for curve in las.curves])

# Extract well name and well number from LAS metadata
well_name = las.well.get("WELL", "Unknown Well").value
company_name = las.well.get("COMP", "Unknown Company").value
well_number = las.well.get("UWI", las.well.get("API", "Unknown Number")).value

# Assign logs dynamically
gr_mnemonic, gr = get_best_log(data_dict["GR"])
pef_mnemonic, pef = get_best_log(data_dict["PEF"])
DResistivity_mnemonic, Dresistivity = get_best_log(data_dict["DeepRes"])
MResistivity_mnemonic, Mresistivity = get_best_log(data_dict["MedRes"])
SResistivity_mnemonic, Sresistivity = get_best_log(data_dict["ShalRes"])
neutron_porosity_mnemonic, neutron_porosity = get_best_log(data_dict["NPHI"])
sonic_porosity_mnemonic, sonic_porosity = get_best_log(data_dict["SPHI"])
density_porosity_mnemonic, density_porosity = get_best_log(data_dict["DPHI"])

# Close any previously open figures
plt.close('all')

# Set up figure
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(12, 12), sharey=True,
                         gridspec_kw={'width_ratios': [0.25, 0.5, 0.5]})
fig.suptitle(company_name+" - "+well_name, fontsize=14, fontweight="bold",ha='right')

# Gamma Ray Track - Cuttoff at 100 API
if gr is not None:
    axes[0].plot(gr, depth, color="black", lw=.25, label=f"GR [{gr_mnemonic}]" if gr_mnemonic else "GR")
axes[0].set_xlabel(f"GR (API)")

# Define track width and create horizontal axis scale
track_left = 0
track_right = 150  # Same as GR x-axis limit

# Create a horizontal span for shading (width = 150)
n_steps = 200  # Controls resolution
x_vals = np.linspace(track_left, track_right, n_steps)
gr_matrix = np.empty((len(depth), n_steps))

# Fill matrix with normalized GR-based shading
for i, g in enumerate(gr):
    gr_matrix[i, :] = g if not np.isnan(g) else 0  # Handle NaNs

# Mask left of the curve
for i, g in enumerate(gr):
    gr_matrix[i, x_vals < g] = np.nan

# Plot the shaded region
cmap = get_cmap("viridis")
norm = Normalize(vmin=0, vmax=150)
axes[0].imshow(
    gr_matrix,
    cmap=cmap,
    norm=norm,
    aspect="auto",
    extent=[track_left, track_right, depth.max(), depth.min()],
    origin="upper"  # <- THIS fixes the vertical flipping
)

axes[0].set_xlim(0, 150)
axes[0].grid()
axes[0].legend()

# Resistivity Track
if Dresistivity is not None:
    axes[1].semilogx(Dresistivity, depth, linestyle=":", color="red", lw=1, label=f"Deep Resistivity [{DResistivity_mnemonic}]" if DResistivity_mnemonic else "Deep Resistivity")
    axes[1].fill_betweenx(depth, 20, Dresistivity, where=(Dresistivity < 20), color="lightblue", alpha=0.5)
    axes[1].fill_betweenx(depth, 20, Dresistivity, where=(Dresistivity > 20), color="yellow", alpha=0.5)
if Mresistivity is not None:
    axes[1].semilogx(Mresistivity, depth, linestyle="--", color="blue", lw=.25, label=f"Medium Resistivity[{MResistivity_mnemonic}]" if MResistivity_mnemonic else "Medium Resistivity")
if Sresistivity is not None:
    axes[1].semilogx(Sresistivity, depth, color="black", lw=.1, label=f"Shallow Resistivity[{SResistivity_mnemonic}]" if SResistivity_mnemonic else "Shallow Resistivity")

# Set axis to logarithmic scale with proper formatting
axes[1].set_xscale("log", nonpositive='clip')
axes[1].set_xlim(0.2, 2000)

# Set major ticks and formatter explicitly
major_ticks = [0.2, 2, 20, 200, 2000]
axes[1].set_xticks(major_ticks)
axes[1].xaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{y:g}"))

axes[1].set_xlabel("Resistivity (Ohm·m)")
axes[1].grid(True, which="both", linestyle="--", linewidth=0.2)


# Porosity & PEF Track
ax2 = axes[2].twiny()
if sonic_porosity is not None:
    axes[2].plot(sonic_porosity, depth, color="purple", lw=.5, linestyle="-", label=f"SPhi [{sonic_porosity_mnemonic}]" if sonic_porosity_mnemonic else "SPhi")
if density_porosity is not None:
    axes[2].plot(density_porosity, depth, color="red", lw=.5, linestyle="--", label=f"DPhi [{density_porosity_mnemonic}]" if density_porosity_mnemonic else "DPhi")
if neutron_porosity is not None:
    axes[2].plot(neutron_porosity, depth, color="green", lw=.5, linestyle=":", label=f"NPhi [{neutron_porosity_mnemonic}]" if neutron_porosity_mnemonic else "NPHI")

if pef is not None:
    ax2.plot(pef, depth, color="orange", lw=.100, linestyle="-", label=f"PEF [{pef_mnemonic}]" if pef_mnemonic else "PEF (barns/e)")

# Porosity Track (axes[2])
axes[2].set_xlabel("Porosity (Decimal)")
axes[2].set_xlim(0.3, -0.1)  # Reverse axis: high porosity on the left
axes[2].grid()

# Set major ticks explicitly to match reversed order
porosity_ticks = [0.3, 0.2, 0.1, 0.0, -0.1]
axes[2].set_xticks(porosity_ticks)
axes[2].set_xticklabels([f"{tick:.2f}" for tick in porosity_ticks])

# PEF Track (ax2, top x-axis)
ax2.set_xlabel(f"PEF (barns/e)")
ax2.set_xlim(0, 40)

# Legends
ax2.legend(loc="upper right")
axes[2].legend(loc="lower right")


plt.tight_layout()
plt.subplots_adjust(top=0.95)
plt.show()
