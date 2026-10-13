from common import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
h=df.resample("h").mean(); d=h.resample("D").median()
og=d[["Buero_Rn","Kueche_Rn","Wohnzimmer_Rn","Schlaf_Rn"]].median(axis=1)
# Bild 1: Keller vs Wohnbereich, Phasen
fig,ax=plt.subplots(figsize=(14,5.5))
ax.plot(d.index,d.Technikraum_Rn,label="Technikraum (Keller)",c="tab:purple"); ax.plot(d.index,d.Werkstatt_Rn,label="Werkstatt (Keller)",c="tab:brown",lw=.8)
ax.plot(d.index,d.KuecheSockel_Rn,label="Küche Sockel",c="tab:green",lw=.9); ax.plot(d.index,og,label="Wohnbereich (Median Büro/Küche/Wohnzi./Schlafzi.)",c="tab:blue")
ax.axvspan("2026-04-01","2026-06-17",color="gold",alpha=.2,label="Keller-Fenster offen? (Keller ~9 Bq/m³)")
ax.axvspan("2026-07-31","2026-08-06",color="red",alpha=.2,label="Urlaub")
ax.axvline(pd.Timestamp("2026-08-24"),c="k",ls="--",label="Wendepunkt-Kandidat 23./24.08.")
ax.axhline(300,c="gray",ls=":"); ax.text(pd.Timestamp("2026-03-26"),310,"Referenzwert 300 Bq/m³",fontsize=8)
ax.set_yscale("symlog",linthresh=30); ax.set_ylim(0,450); ax.set_ylabel("Radon, Tagesmedian [Bq/m³]"); ax.legend(fontsize=8,loc="upper left"); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig("bilder/phasen.png",dpi=90); plt.close()
# Bild 2: Urlaub
x=df.loc["2026-07-29":"2026-08-09"].resample("h").mean()
fig,a=plt.subplots(2,1,figsize=(14,6),sharex=True)
for c in ["Buero_Rn","Kueche_Rn","KuecheSockel_Rn","Schlaf_Rn","Technikraum_Rn","Werkstatt_Rn","Wohnzimmer_Rn"]: a[0].plot(x.index,x[c],lw=.9,label=c[:-3])
a[0].legend(ncol=7,fontsize=8); a[0].set_ylabel("Radon [Bq/m³]"); a[0].grid(alpha=.3)
a[1].plot(x.index,x["KuecheL_CO₂_(ppm)"],label="CO₂ Küche"); a[1].plot(x.index,x["Schlaf_CO₂_(ppm)"],label="CO₂ Schlafzimmer"); a[1].legend(); a[1].set_ylabel("ppm"); a[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig("bilder/urlaub.png",dpi=90); plt.close()
# Bild 3: Keller-Sägezahn Jul-Sep
x=h.loc["2026-06-15":"2026-09-30"]
fig,a=plt.subplots(figsize=(14,4.5))
a.plot(x.index,x.Technikraum_Rn.rolling(3,min_periods=1).mean(),label="Technikraum"); a.plot(x.index,x.Werkstatt_Rn.rolling(3,min_periods=1).mean(),label="Werkstatt",lw=.8); a.plot(x.index,x.KuecheSockel_Rn.rolling(3,min_periods=1).mean(),label="Küche Sockel",lw=.8)
a.plot(x.index,x[["Buero_Rn","Kueche_Rn","Wohnzimmer_Rn"]].median(axis=1).rolling(3,min_periods=1).mean(),label="Wohnbereich",lw=.8,c="tab:blue")
for t,l in [("2026-07-17","17.07."),("2026-08-14","14.08."),("2026-08-24","24.08.")]: a.axvline(pd.Timestamp(t),c="k",ls=":"); a.text(pd.Timestamp(t),345,l,fontsize=8)
a.legend(ncol=4); a.set_ylabel("Radon [Bq/m³]"); a.grid(alpha=.3); plt.tight_layout(); plt.savefig("bilder/keller_saegezahn.png",dpi=90)
