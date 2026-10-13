from common import *
import sys
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
a,b,f=sys.argv[1],sys.argv[2],sys.argv[3]
c=["Buero_Rn","Kueche_Rn","KuecheSockel_Rn","Schlaf_Rn","Technikraum_Rn","Werkstatt_Rn","Wohnzimmer_Rn","KuecheL_CO₂_(ppm)","Schlaf_CO₂_(ppm)","W_Temperatur_2_m_(°C)"]
x=df[c].resample(f).mean().loc[a:b].round(0)
x.columns=["Bu","Kü","Sock","Schl","Tech","Werk","Wohn","CO2K","CO2S","Taus"]
print(x.to_string())
