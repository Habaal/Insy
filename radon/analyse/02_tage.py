from common import *
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn").replace("_(ppm)","").replace("_(°C)","").replace("_(hPa)","") for c in df.columns]
rn=[c for c in df.columns if c.endswith("_Rn")]
d=df[rn].resample("D").median().round(0)
d["CO2_K_max"]=df["KuecheL_CO₂"].resample("D").max()
d["CO2_K_min"]=df["KuecheL_CO₂"].resample("D").min()
d["CO2_S_max"]=df["Schlaf_CO₂"].resample("D").max()
d["T_aussen"]=df["W_Temperatur_2_m"].resample("D").mean().round(1)
d["T_Schlaf"]=df["Schlaf_Temperatur_innen"].resample("D").mean().round(1)
d.to_csv("analyse/tageswerte.csv")
import sys
a,b=sys.argv[1],sys.argv[2]
print(d.loc[a:b])
