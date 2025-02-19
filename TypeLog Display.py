import lasio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Dictionary mapping common log mnemonics
data_dict = {
    "ROP": ["ROP", "10FTRATE", "10FTROP", "5FTRATE", "5FTROP", "DR", "DRILLRATE", "FTPERHR", "ROP:1", "ROP:2", "ROPI", "ROPTVD"],
    "Cal": ["Cal", "CAL1", "CAL2", "CAL3", "CAL4", "CAL5", "CAL6", "CAL7", "CALD", "CALI", "CALIFLG", "CALR", "CALS", "CALX", "CALXD", "CALXR", "CALYD"],
    "GR": ["GR", "CGR", "CGRD", "ECGR", "ECGR_TMG", "GR_EDTC", "GR_TMG", "GRC", "GRCM", "GRCO", "GRCX", "GRD", "GRFET", "GRGC", "GRR", "GRS", "GRTO", "GRW", "HCGR", "HGR", "HSGR", "MWD-GR", "NATURAL_GAMMA", "SGR", "SGRDD", "GAMMA"],
    "SP": ["SP", "SPR"],
    "RHOB": ["RHOB", "ZDEN", "RHOBEDIT", "RHOL", "RHOZ"],
    "DPHI": ["DPHI", "CDL_LS", "DPDL", "DPH8", "DPHD", "DPHI_LS", "DPHIL", "DPHIVV", "DPHZ", "DPLS", "DPRL", "PORD", "PORZ", "PORZC_LS", "PRZC", "DPHS"],
    "NPHI": ["NPHI", "CNLS", "CNPORU", "CNS_LS", "DNPH", "HNPO", "HTNP", "NLIM", "NPDL", "NPHI_LS", "NPHL", "NPLS", "NPOR", "NPRL", "TNPH", "TNPH_LIM"],
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
las_file_path = r"C:\Python3.12\Scripts\LAS Tools\s_f0995ae8200960e0529ffa8d68ea3035.las"
tops_file_path = r"C:\Python3.12\Scripts\LAS Tools\TestTops.csv"

# Load LAS file
las = lasio.read(las_file_path)
depth = las.index

print([curve.mnemonic for curve in las.curves])

# Extract well name and well number from LAS metadata
well_name = las.well.get("WELL", "Unknown Well").value
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

# Load formation tops
tops_df = pd.read_csv(tops_file_path)
tops_df["Depth"] = pd.to_numeric(tops_df["Depth"], errors="coerce")

# Close any previously open figures
plt.close('all')

# Set up figure
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(12, 12), sharey=True,
                         gridspec_kw={'width_ratios': [0.25, 0.5, 0.5]})
fig.suptitle(well_name, fontsize=14, fontweight="bold")

# Gamma Ray Track
if gr is not None:
    axes[0].plot(gr, depth, color="black", lw=.25, label="Gamma Ray (API)")
axes[0].set_xlabel("GR (API)")
axes[0].fill_betweenx(depth, 100, gr, where=(gr < 100), color="lightblue", alpha=0.5)
axes[0].fill_betweenx(depth, 100, gr, where=(gr > 100), color="tan", alpha=0.5)
axes[0].set_xlim(0, 150)
axes[0].invert_yaxis()
axes[0].grid()
axes[0].legend()

# Resistivity Track
if Dresistivity is not None:
    axes[1].semilogx(Dresistivity, depth, linestyle=":", color="red", lw=1, label="Deep Resistivity")
    axes[1].fill_betweenx(depth, 20, Dresistivity, where=(Dresistivity < 20), color="lightblue", alpha=0.5)
    axes[1].fill_betweenx(depth, 20, Dresistivity, where=(Dresistivity > 20), color="yellow", alpha=0.5)
if Mresistivity is not None:
    axes[1].semilogx(Mresistivity, depth, linestyle="--", color="blue", lw=.25, label="Medium Resistivity")
if Sresistivity is not None:
    axes[1].semilogx(Sresistivity, depth, color="black", lw=.1, label="Shallow Resistivity")

axes[1].set_xlabel("Resistivity (Ohm.m)")
axes[1].set_xlim(0.2, 2000)
axes[1].set_xticks([0.2, 2, 20, 200, 2000])
axes[1].grid(which="both")
axes[1].legend()

# Porosity & PEF Track
ax2 = axes[2].twiny()
if density_porosity is not None and neutron_porosity is not None and sonic_porosity is not None:
    axes[2].plot(sonic_porosity, depth, color="purple", lw=.25, linestyle="-", label="Sonic Porosity")
    axes[2].plot(density_porosity, depth, color="red", lw=.25, linestyle="--", label="Density Porosity")
    axes[2].plot(neutron_porosity, depth, color="green", lw=.25, linestyle=":", label="Neutron Porosity")
if pef is not None:
    ax2.plot(pef, depth, color="blue", lw=.100, linestyle="-", label="PEF")

axes[2].set_xlabel("Porosity (Fraction)")
axes[2].set_xlim(0.3, -0.1)
axes[2].grid()
ax2.set_xlabel("PEF (barns/e)")
ax2.set_xlim(0, 40)
axes[2].set_xticks(np.linspace(-0.1, 0.3, 10))  # Increase number of vertical grid lines
axes[2].set_xticklabels([f"{tick:.2f}" for tick in np.linspace(-0.1, 0.3, 10)], rotation=90)  # Rotate labels
ax2.legend(loc="upper right")
axes[2].legend(loc="lower right")

# Overlay formation tops if available
if tops_df is not None:
    for _, row in tops_df.iterrows():
        for ax in axes:
            ax.axhline(y=row["Depth"], color="black", linewidth=1)
        axes[0].text(5, row["Depth"], row["TopName"], verticalalignment="bottom",
                     color="black", fontsize=10, fontweight="bold")

plt.tight_layout()
plt.subplots_adjust(top=0.95)
plt.show()
