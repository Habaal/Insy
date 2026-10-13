from common import *
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
h=df.resample("h").mean()
w=h["W_Luftdruck_(hPa)"].interpolate(limit=3)
x=pd.DataFrame({"dK":h["KuecheL_Luftdruck_innen_(hPa)"]-w,"dS":h["Schlaf_Luftdruck_innen_(hPa)"]-w})
x["dKS"]=h["KuecheL_Luftdruck_innen_(hPa)"]-h["Schlaf_Luftdruck_innen_(hPa)"]
d=x.resample("D").agg(["mean","std"]).round(2)
print(d.resample("W").mean().round(2))
x.to_csv("analyse/druckdiff_stuendlich.csv")
