from common import *
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
h=df.resample("h").mean()
OG=h[["Buero_Rn","Kueche_Rn","Wohnzimmer_Rn","Schlaf_Rn"]].mean(axis=1)
co2s=h["Schlaf_CO₂_(ppm)"]; ta=h["W_Temperatur_2_m_(°C)"]; tin=h["Schlaf_Temperatur_innen_(°C)"]
INST=pd.Timestamp("2026-08-24")
# --- B) Nacht-Anreicherung: 21-22 Uhr bis 06-07 Uhr
rows=[]
for d in pd.date_range("2026-05-14","2026-10-12"):
    a=d+pd.Timedelta(hours=21); b=d+pd.Timedelta(hours=30)
    try: r0=OG.loc[a:a+pd.Timedelta(hours=1)].mean(); r1=OG.loc[b-pd.Timedelta(hours=1):b].mean(); c0=co2s.loc[a:a+pd.Timedelta(hours=1)].mean(); c1=co2s.loc[b-pd.Timedelta(hours=1):b].mean()
    except Exception: continue
    rows.append(dict(tag=d,Rn_abend=r0,Rn_frueh=r1,dRn=r1-r0,CO2_abend=c0,dCO2=c1-c0,Taus=ta.loc[a:b].mean(),dT=(tin.loc[a:b]-ta.loc[a:b]).mean()))
n=pd.DataFrame(rows).dropna(); n=n[~((n.tag>="2026-07-31")&(n.tag<="2026-08-06"))]
n["phase"]=np.where(n.tag<INST,"vor Einbau","nach Einbau")
n["geschlossen"]=n.dCO2>=250
print("Naechte gesamt:",len(n)); print(n.groupby(["phase","geschlossen"]).agg(naechte=("dRn","size"),dRn_med=("dRn","median"),dRn_mean=("dRn","mean"),frueh_med=("Rn_frueh","median"),frueh_P90=("Rn_frueh",lambda s:s.quantile(.9)),dCO2=("dCO2","median"),Taus=("Taus","mean"),dT=("dT","mean")).round(1).to_string())
# Nur Juni-Aug vor Einbau gegen nach Einbau, gleiche Aussentemperatur-Spanne
m=n[(n.tag>="2026-06-01")]; print("\nvergleichbare Aussentemp 12-20 Grad, geschlossen:"); mm=m[(m.Taus.between(12,20))&m.geschlossen]
print(mm.groupby("phase").agg(naechte=("dRn","size"),dRn_med=("dRn","median"),frueh_med=("Rn_frueh","median"),frueh_max=("Rn_frueh","max"),Taus=("Taus","mean")).round(1).to_string())
n.to_csv("analyse/naechte.csv",index=False)
# --- C) Spitzen: OG-Mittel steigt >=2x in <=4h auf >=45 und faellt danach >=40% in <=3h
ev=[]; v=OG
i=0; idx=v.index
vals=v.values
for k in range(4,len(vals)-3):
    if np.isnan(vals[k]) or vals[k]<45: continue
    if not (vals[k]>=vals[k-1] and vals[k]>=vals[k+1]): continue
    lo=np.nanmin(vals[k-4:k]); hi=np.nanmin(vals[k+1:k+4])
    if lo*2<=vals[k] and hi<=vals[k]*0.6: ev.append((idx[k],vals[k],lo,hi))
e=pd.DataFrame(ev,columns=["t","peak","vorher","danach"]); e=e[~((e.t>="2026-07-31")&(e.t<"2026-08-07"))]
e["phase"]=np.where(e.t<INST,"vor Einbau",np.where(e.t<INST+pd.Timedelta(days=7),"1. Woche nach Einbau","danach"))
tage={"vor Einbau":(INST-pd.Timestamp("2026-05-14")).days-6,"1. Woche nach Einbau":7,"danach":(pd.Timestamp("2026-10-13")-INST).days-7}
g=e.groupby("phase").agg(n=("peak","size"),peak_med=("peak","median"),peak_max=("peak","max"),vorher_med=("vorher","median")).round(0); g["tage"]=pd.Series(tage); g["pro_woche"]=(g.n/g.tage*7).round(1); print("\nSpitzen-Ereignisse (ab 14.05.)"); print(g.to_string())
print(e[e.t>=INST-pd.Timedelta(days=1)].round(0).to_string())
# --- D) Beitrag der Spitzen zur mittleren Belastung (nur Wohnbereich, ohne Urlaub)
vv=OG[(OG.index>="2026-04-01")]; vv=vv[~((vv.index>="2026-07-31 18:00")&(vv.index<"2026-08-07"))]
pre=vv[vv.index<INST].dropna(); post=vv[vv.index>=INST].dropna()
for nm,s in [("vor",pre),("nach",post)]:
    ex=(s-30).clip(lower=0)  # Anteil ueber 30 (Messgenauigkeit)
    print(nm,"Mittel",round(s.mean(),1),"Std",len(s),"Anteil der Stunden >60:",round(100*(s>60).mean(),1),"%  Mittelwert ohne Stunden >60:",round(s[s<=60].mean(),1))
