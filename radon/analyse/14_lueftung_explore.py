from common import *
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
h=df.resample("h").mean()
og=h[["Buero_Rn","Kueche_Rn","Wohnzimmer_Rn","Schlaf_Rn"]]
x=pd.DataFrame({"OG_mean":og.mean(axis=1),"OG_max_room":og.max(axis=1),"Sock":h.KuecheSockel_Rn,"CO2K":h["KuecheL_CO₂_(ppm)"],"CO2S":h["Schlaf_CO₂_(ppm)"]})
d=x.resample("D").agg({"OG_mean":["mean","max"],"OG_max_room":"max","Sock":"max","CO2K":["min","max"],"CO2S":["min","max"]}).round(0)
d.columns=["OGmean","OGmeanMax","RoomMax","SockMax","CO2Kmin","CO2Kmax","CO2Smin","CO2Smax"]
print(d.loc["2026-08-17":"2026-09-14"].to_string())
print(d.loc["2026-09-15":"2026-10-13"].resample("W").mean().round(0).to_string())
