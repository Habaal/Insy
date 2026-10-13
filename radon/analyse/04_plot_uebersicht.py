from common import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
rn=[c for c in df.columns if c.endswith("_Rn")]
h=df.resample("h").median()
fig,ax=plt.subplots(4,1,figsize=(18,16),sharex=True)
for c in rn: ax[0].plot(h.index,h[c].rolling(6,min_periods=1).mean(),lw=.8,label=c[:-3])
ax[0].set_yscale("log"); ax[0].set_ylabel("Radon Bq/m³ (log)"); ax[0].legend(ncol=7,fontsize=8); ax[0].grid(alpha=.3)
ax[1].plot(h.index,h["KuecheL_CO₂_(ppm)"],lw=.5,label="CO2 Küche"); ax[1].plot(h.index,h["Schlaf_CO₂_(ppm)"],lw=.5,label="CO2 Schlafzimmer"); ax[1].legend(); ax[1].grid(alpha=.3)
ax[2].plot(h.index,h["KuecheL_Luftdruck_innen_(hPa)"],lw=.6,label="innen Küche"); ax[2].plot(h.index,h["Schlaf_Luftdruck_innen_(hPa)"],lw=.6,label="innen Schlaf"); ax[2].plot(h.index,h["W_Luftdruck_(hPa)"],lw=.6,label="außen"); ax[2].legend(); ax[2].grid(alpha=.3); ax[2].set_ylabel("hPa")
ax[3].plot(h.index,h["W_Temperatur_2_m_(°C)"],lw=.6,label="außen 2m"); ax[3].plot(h.index,h["Schlaf_Temperatur_innen_(°C)"],lw=.6,label="Schlaf innen"); ax[3].plot(h.index,h["KuecheL_Temperatur_innen_(°C)"],lw=.6,label="Küche innen");ax[3].legend(); ax[3].grid(alpha=.3)
plt.tight_layout(); plt.savefig("bilder/uebersicht.png",dpi=80)
