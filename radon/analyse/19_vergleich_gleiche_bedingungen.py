"""Vorher/Nachher bei gleicher Außentemperatur (Nachtwerte 2-6 Uhr) + Lüften-Fit-Check."""
from common import *
from scipy.optimize import curve_fit
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
h=df.resample("h").mean()
OG=h[["Buero_Rn","Kueche_Rn","Wohnzimmer_Rn","Schlaf_Rn"]].mean(axis=1); Tout=h["W_Temperatur_2_m_(°C)"]; Wind=h["W_Wind_10_m_(km/h)"]
INST=pd.Timestamp("2026-08-24"); U0,U1=pd.Timestamp("2026-07-31 18:00"),pd.Timestamp("2026-08-06 19:30")
rows=[]
for d in pd.date_range("2026-04-01","2026-10-12"):
    a,b=d+pd.Timedelta(hours=2),d+pd.Timedelta(hours=6)
    if ((h.index>=U0-pd.Timedelta(hours=24))&(h.index<U1+pd.Timedelta(hours=24))&(h.index>=a)&(h.index<=b)).any(): continue
    rows.append(dict(d=d,og=OG.loc[a:b].mean(),tout=Tout.loc[a:b].mean(),wind=Wind.loc[a:b].mean(),post=d>=INST))
W=pd.DataFrame(rows).dropna()
W["bin"]=pd.cut(W.tout,[-5,6,9,12,15,18,21,30])
g=W.groupby(["bin","post"],observed=True).og.agg(["count","median","mean"]).round(1).unstack("post")
print(g.to_string())
# gleiche Bedingungen: Tout 6-15 Grad, Nachtwind
for lo,hi in [(6,12),(9,15)]:
    s=W[(W.tout>=lo)&(W.tout<hi)]
    a,b=s[~s.post].og,s[s.post].og
    print(f"Tout {lo}-{hi}: vor n={len(a)} Median {a.median():.1f} (P75 {a.quantile(.75):.1f}) | nach n={len(b)} Median {b.median():.1f} (P75 {b.quantile(.75):.1f})")
# Hoehere Spitzen bei gleicher Temperatur: Anteil Naechte mit OG>60
for lo,hi in [(6,15)]:
    s=W[(W.tout>=lo)&(W.tout<hi)]; print("Anteil Nächte Mittel>60:", round(100*(s[~s.post].og>60).mean(),1), round(100*(s[s.post].og>60).mean(),1))
# Lueften nach Rueckkehr: Fit mit Schranken
og10=df[["Buero_Rn","Kueche_Rn","Wohnzimmer_Rn","Schlaf_Rn"]].resample("10min").mean().mean(axis=1)
x=og10.loc["2026-08-06 19:00":"2026-08-07 02:00"]; print(x.round(0).to_string()[:900])
