from common import *
df=laden(); df.columns=[kurz(c) for c in df.columns]
print(list(df.columns))
rn=[c for c in df.columns if c.endswith("_Rn")]
# Nullwerte / Resets
for c in rn:
    bz=c[:-3]+"_BZ"
    s=df[c].dropna(); b=df[bz].dropna()
    resets=(b.diff()<0).sum()
    print(c,"n=",len(s),"Nullwerte=",(s==0).sum(),"BZ-Resets=",resets,"Median=",s[s>0].median())
w=df[rn].resample("W").median().round(0)
print(w)
