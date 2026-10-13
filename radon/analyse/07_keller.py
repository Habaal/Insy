from common import *
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
h=df[[c for c in df.columns if c.endswith("_Rn")]].resample("h").mean()
d=pd.DataFrame({
 "Tech_min":h.Technikraum_Rn.resample("D").min(),"Tech_med":h.Technikraum_Rn.resample("D").median(),"Tech_max":h.Technikraum_Rn.resample("D").max(),
 "Werk_med":h.Werkstatt_Rn.resample("D").median(),
 "Sock_med":h.KuecheSockel_Rn.resample("D").median(),
 "Obergeschoss_med":h[["Buero_Rn","Kueche_Rn","Wohnzimmer_Rn"]].median(axis=1).resample("D").median()}).round(0)
d["Tech/OG"]=(d.Tech_med/d.Obergeschoss_med).round(2)
print(d.loc["2026-04-01":"2026-07-20"].to_string())
