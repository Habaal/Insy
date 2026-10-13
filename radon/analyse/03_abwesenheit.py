from common import *
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
k=df["KuecheL_CO₂_(ppm)"].resample("D").agg(["min","max","mean"]); s=df["Schlaf_CO₂_(ppm)"].resample("D").agg(["min","max","mean"])
x=pd.DataFrame({"K_min":k["min"],"K_max":k["max"],"K_amp":k["max"]-k["min"],"S_min":s["min"],"S_max":s["max"],"S_amp":s["max"]-s["min"]}).round(0)
x["ruhig"]=(x.K_amp<150)&(x.S_amp<150)
print(x[x.ruhig|(x.K_max<600)])
print("Tage CO2 gesamt:",x.K_amp.notna().sum())
