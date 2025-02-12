import lasio
import numpy as np
import matplotlib.pyplot as plt

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
    "DeepRes": ["ILD", "90IN_4FT_R", "90IN_4FT_R_S", "AHT90", "AT90", "ATCO90", "RILD", "RLA5", "RO90", "DDLL", "DEEP_RESISTIVITY", "HLLD", "IDPH", "LGRD", "RD", "RESISTIVITY_(SHORT-SPACING)", "RESISTIVITY", "RESISTIVITY_(LONG-SPACING)", "RESISTIVITY_(SHORT-SPACING)", "RESITIVITY_(SHORT-SPACING)", "RILD", "RLA5", "RO90", "RT90"],
    "MedRes": ["ILM", "LLM", "AHT60", "60IN_4FT_R", "IMPH", "RF60", "RILM", "RLA3", "RMLL", "RO60", "RT60"],
    "ShalRes": ["RXO", "RXO8", "RXOZ", "RXO_HRLT", "RXRT", "SFLU", "SGRD", "SHORT_RESISTIVITY", "DSLL", "HLLS", "RLA1", "RS", "RSOZ", "RT10", "AHT10", "AT30", "RF10", "RO10"]
}


# Function to find the best log
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

# Prompt user to enter the LAS file path
# directory = input("Enter directory: ")
# file_name = input("Enter the file name (sans file type): ")
# las_file_path = directory+"/"+file_name+".las"
las_file_path = r"L:\Geologic Data\Logs\LAS\TRRC\s_db2db6ae484123edd83068d0b11c1b83.las"

# Load the LAS file
las = lasio.read(las_file_path)

# Extract depth values
depth = las.index  

# Assign logs dynamically
gr_mnemonic, gr = get_best_log(data_dict["GR"])
pef_mnemonic, pef = get_best_log(data_dict["PEF"])
DResistivity_mnemonic, Dresistivity = get_best_log(data_dict["DeepRes"])
MResistivity_mnemonic, Mresistivity = get_best_log(data_dict["MedRes"])
SResistivity_mnemonic, Sresistivity = get_best_log(data_dict["ShalRes"])
neutron_porosity_mnemonic, neutron_porosity = get_best_log(data_dict["NPHI"])
density_porosity_mnemonic, density_porosity = get_best_log(data_dict["DPHI"])

# Set up figure with custom widths
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(12, 12), sharey=True,
                         gridspec_kw={'width_ratios': [0.25, 0.5, 0.5]})
fig.suptitle("Petrophysical Logs", fontsize=14, fontweight="bold")

# Gamma Ray Track
if gr is not None:
    axes[0].plot(gr, depth, color="black", lw=1, label="Gamma Ray (API)")
axes[0].set_xlabel("GR (API)")
axes[0].set_xlim(0, 150)
axes[0].invert_yaxis()  # Depth increases downward
axes[0].grid()
axes[0].legend()

# Resistivity Track (Log Scale) with Shading
if Dresistivity is not None:
    axes[1].semilogx(Dresistivity, depth, linestyle=":", color="red", lw=1, label="Deep Resistivity")
if Mresistivity is not None:
    axes[1].semilogx(Mresistivity, depth, linestyle="--", color="blue", lw=1, label="Medium Resistivity")
if Sresistivity is not None:
    axes[1].semilogx(Sresistivity, depth, color="black", lw=1, label="Shallow Resistivity")

    # Add shading between the DeepRes and 20 ohms
    axes[1].fill_betweenx(depth, Dresistivity, 20, where=(Dresistivity <= 20), color="lightblue", alpha=0.5, label="DRes < 20 Ohm.m")

axes[1].set_xlabel("Resistivity (Ohm.m)")
axes[1].set_xlim(0.2, 2000)
axes[1].set_xticks([0.2, 2, 20, 200, 2000])
axes[1].set_xticklabels(["0.2", "2", "20", "200", "2000"])
axes[1].grid(which="both")
axes[1].legend()

# Porosity & PEF Track (Reversed X-axis + Secondary Axis)
ax2 = axes[2].twiny()  # Create secondary x-axis for PEF

if density_porosity is not None and neutron_porosity is not None:
    axes[2].plot(density_porosity, depth, color="red", lw=1, linestyle="--", label="Density Porosity")
    axes[2].plot(neutron_porosity, depth, color="green", lw=1, linestyle=":", label="Neutron Porosity")

    # Add shading where Density Porosity > Neutron Porosity
    axes[2].fill_betweenx(depth, neutron_porosity, density_porosity, 
                          where=(density_porosity > neutron_porosity),
                          color="pink", alpha=0.5, label="DPHI > NPHI")

if pef is not None:
    ax2.plot(pef, depth, color="blue", lw=1, linestyle="-", label="PEF")

# Primary axis (Porosity)
axes[2].set_xlabel("Porosity (Fraction)")
axes[2].set_xlim(0.3, -0.1)  # Reverse x-axis
axes[2].grid()

# Secondary axis (PEF)
ax2.set_xlabel("PEF (barns/e)")
ax2.set_xlim(0, 40)  
ax2.spines["top"].set_visible(True)  # Ensure secondary axis is visible
ax2.tick_params(axis="x", which="both", direction="out")  
ax2.legend(loc="upper right")

axes[2].legend(loc="lower right")

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.95)

plt.show()