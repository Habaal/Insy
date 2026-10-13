from common import *
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
print("Zeilen:",len(df),"doppelte Zeitstempel:",df.index.duplicated().sum())
for c in [c for c in df.columns if c.endswith("_Rn")]+["KuecheL_CO₂_(ppm)","Schlaf_CO₂_(ppm)","W_Temperatur_2_m_(°C)"]:
    s=df[c].dropna(); dt=s.index.to_series().diff().dropna()
    med=dt.median(); big=dt[dt>pd.Timedelta("2h")].sort_values(ascending=False).head(3)
    print(f"{c:26s} Intervall-Median={med}  Luecken>2h: {(dt>pd.Timedelta('2h')).sum()}  groesste: "+", ".join(f"{v} ab {i-v:%d.%m. %H:%M}" for i,v in big.items()))
# Luecken über alle Radon-Sensoren
rn=[c for c in df.columns if c.endswith("_Rn")]
anyv=df[rn].dropna(how="all").index.to_series().diff().dropna()
print("Luecken > 1h ueber ALLE Radon-Sensoren:"); print(anyv[anyv>pd.Timedelta("1h")].sort_values(ascending=False).head(10))
for c in rn:
    s=df[c].dropna()
    # Plateau: gleicher Wert >=? Mal in Folge
    print(c,"negativ:",(s<0).sum(),"nicht ganzzahlig:",(s%1>0).sum(), "max:",s.max(), "@",s.idxmax())
