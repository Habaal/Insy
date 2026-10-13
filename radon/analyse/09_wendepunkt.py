from common import *
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
rn=[c for c in df.columns if c.endswith("_Rn")]
h=df[rn].resample("h").mean()
d=np.log1p(h).resample("D").mean()   # log-Mittel pro Tag
def best_split(s,a,b):
    s=s.loc[a:b].dropna(); s=s.drop(s.loc["2026-07-31":"2026-08-07"].index,errors="ignore"); best=None
    for i in range(10,len(s)-10):
        l,r=s.iloc[:i],s.iloc[i:]
        sse=((l-l.mean())**2).sum()+((r-r.mean())**2).sum()
        if best is None or sse<best[0]: best=(sse,s.index[i],np.expm1(l.mean()),np.expm1(r.mean()))
    return best
print("Beste Einzel-Trennung je Sensor, Zeitraum 15.07.-13.10. (geometr. Mittel Bq/m3 vorher/nachher)")
for c in rn:
    b=best_split(d[c],"2026-07-15","2026-10-13"); print(f"{c:18s} {b[1].date()}  {b[2]:.0f} -> {b[3]:.0f}")
print("\nTechnikraum+Werkstatt, Zeitraum 01.06.-01.08. (Fenster zu?)")
for c in ["Technikraum_Rn","Werkstatt_Rn"]:
    b=best_split(d[c],"2026-06-01","2026-07-25"); print(f"{c:18s} {b[1].date()}  {b[2]:.0f} -> {b[3]:.0f}")
# Vergleich Perioden
per={"A 01.04.-17.06.":("2026-04-01","2026-06-17"),"B 22.06.-31.07.":("2026-06-22","2026-07-31"),"Urlaub 02.-06.08.":("2026-08-02","2026-08-06"),"C 07.08.-23.08.":("2026-08-07","2026-08-23"),"D 25.08.-24.09.":("2026-08-25","2026-09-24"),"E 25.09.-13.10.":("2026-09-25","2026-10-13")}
print("\nMedian Bq/m3 je Periode")
t={k:h.loc[a:b].median().round(0) for k,(a,b) in per.items()}
print(pd.DataFrame(t).T.to_string())
