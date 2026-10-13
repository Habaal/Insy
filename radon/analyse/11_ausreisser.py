from common import *
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
rn=[c for c in df.columns if c.endswith("_Rn")]
h=df[rn].resample("h").mean()
base=h.rolling(24*7,center=True,min_periods=24*3).median()
flag=(h>3*base+30)&(h>100)
flag["ALLE"]=flag[["Buero_Rn","Kueche_Rn","Wohnzimmer_Rn","Schlaf_Rn"]].sum(axis=1)
# Ereignisse: zusammenhaengende Stunden mit >=1 Raum geflaggt (Luecken <=3h überbrücken)
any_=flag[rn].any(axis=1)
ev=[];start=None;last=None
for t,v in any_.items():
    if v:
        if start is None: start=t
        elif (t-last)>pd.Timedelta("3h"): ev.append((start,last)); start=t
        last=t
if start is not None: ev.append((start,last))
rows=[]
for a,b in ev:
    seg=h.loc[a:b]; fl=flag.loc[a:b,rn].any()
    rows.append({"von":a,"bis":b+pd.Timedelta("1h"),"Std":int((b-a)/pd.Timedelta("1h"))+1,"Raeume":",".join(c[:-3] for c in rn if fl[c]),"Peak":int(seg[rn].max().max()),"Peak_Raum":seg[rn].max().idxmax()[:-3]})
e=pd.DataFrame(rows); e.to_csv("analyse/ereignisse_radon.csv",index=False)
print(len(e),"Ereignisse"); print(e.to_string())
