from common import *
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
h=df.resample("h").mean()
OG=["Buero_Rn","Kueche_Rn","Wohnzimmer_Rn","Schlaf_Rn"]
INST=pd.Timestamp("2026-08-24")
x=pd.DataFrame({"OG":h[OG].mean(axis=1),"OGmax":h[OG].max(axis=1),"Sock":h.KuecheSockel_Rn,"Kue":h.Kueche_Rn,"Wohn":h.Wohnzimmer_Rn,"Buero":h.Buero_Rn,
                "CO2K":h["KuecheL_CO₂_(ppm)"],"Taus":h["W_Temperatur_2_m_(°C)"],"Tin":h["KuecheL_Temperatur_innen_(°C)"]})
x["Sock_minus_Kue"]=x.Sock-x.Kue
urlaub=(x.index>="2026-07-31 18:00")&(x.index<"2026-08-07")
start=x.index<"2026-04-01"
v=x[~urlaub&~start]
def stat(s): return pd.Series({"Std":s.OG.count(),"OG_mean":s.OG.mean(),"OG_median":s.OG.median(),"OG_P95":s.OG.quantile(.95),"OGmax_P99":s.OGmax.quantile(.99),
  "h_OGmax>100":(s.OGmax>100).sum(),"%h>100":100*(s.OGmax>100).mean(),"h_OGmax>60":(s.OGmax>60).sum(),
  "Sock-Kue_med":s.Sock_minus_Kue.median(),"Sock_med":s.Sock.median(),"Kue_med":s.Kue.median()})
pre=v[v.index<INST]; post=v[v.index>=INST]
print(pd.DataFrame({"vor 24.08. (ohne Urlaub)":stat(pre),"ab 24.08.":stat(post),"ab 24.08. bis 22.09.":stat(post[post.index<"2026-09-23"]),"ab 23.09.":stat(post[post.index>="2026-09-23"])}).round(1).to_string())
print("\nMit Urlaub, ganzer Zeitraum ab 01.04. vor Einbau: OG_mean",round(x[(x.index>='2026-04-01')&(x.index<INST)].OG.mean(),1))
w=v.resample("W").apply(lambda s:None) if False else None
wk=pd.DataFrame({"OG_med":v.OG.resample("W").median(),"OG_P95":v.OG.resample("W").quantile(.95),"h>100":(v.OGmax>100).resample("W").sum(),
  "Sock-Kue":v.Sock_minus_Kue.resample("W").median(),"Wohn-Kue":(v.Wohn-v.Kue).resample("W").median(),"Buero-Kue":(v.Buero-v.Kue).resample("W").median(),"CO2Kmin_med":v.CO2K.resample("D").min().resample("W").median()}).round(1)
print(wk.loc["2026-04-05":].to_string())
