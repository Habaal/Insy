from common import *
df=laden(); df.columns=[kurz(c) for c in df.columns]
ev=[]
for r in ["Buero","Kueche","KuecheSockel","Technikraum","Werkstatt","Wohnzimmer"]:
    b=df[r+"_BZ"].dropna()
    m=b.diff()<-5
    for t,v,p in zip(b.index[m],b[m],b.shift()[m]): ev.append((t.floor("h"),r,int(p),int(v)))
e=pd.DataFrame(ev,columns=["t","raum","bz_vorher","bz_nachher"]).sort_values("t")
print(e.to_string())
