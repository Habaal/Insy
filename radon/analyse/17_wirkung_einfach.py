"""Bilder fuer Laien + Wirkungsanalyse der Ueberdruck-Anlage (Einbau 24.08.2026)."""
from common import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":13,"axes.titlesize":16,"axes.titleweight":"bold","axes.spines.top":False,"axes.spines.right":False,"font.family":"DejaVu Sans"})
BLAU,ORANGE,GRAU,GRUEN,GELB,ROT="#2a78d6","#eb6834","#898781","#2e9e4f","#eda100","#d03b3b"
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
h=df.resample("h").mean()
OGc=["Buero_Rn","Kueche_Rn","Wohnzimmer_Rn","Schlaf_Rn"]
OG=h[OGc].mean(axis=1); OGmax=h[OGc].max(axis=1)
INST=pd.Timestamp("2026-08-24"); U0,U1=pd.Timestamp("2026-07-31 18:00"),pd.Timestamp("2026-08-06 19:30")
def ampel(ax,ymax):
    ax.axhspan(0,100,color=GRUEN,alpha=.08); ax.axhspan(100,300,color=GELB,alpha=.12); ax.axhspan(300,ymax,color=ROT,alpha=.10)
    x=ax.get_xlim()[0]
    for y,t,c in [(88,"unbedenklich (unter 100)",GRUEN),(200,"erhöht (100 bis 300)","#9a6b00"),(ymax*.93,"hoch (über 300)",ROT)]:
        ax.text(0.995,y,t,transform=ax.get_yaxis_transform(),ha="right",va="center",color=c,fontsize=11,bbox=dict(fc="white",ec="none",alpha=.7,pad=1.5))
# ---------- Bild 1: Gesamtverlauf einfach
d=OG.resample("D").median(); dmax=OGmax.resample("D").max()
fig,ax=plt.subplots(figsize=(13,6)); ax.set_ylim(0,450); ax.set_xlim(pd.Timestamp("2026-03-24"),pd.Timestamp("2026-10-14"))
ampel(ax,450)
ax.fill_between(d.index,d,dmax.clip(upper=450),color=BLAU,alpha=.18,label="höchster Stundenwert des Tages (ein Raum)")
ax.plot(d.index,d,color=BLAU,lw=2.2,label="typischer Wert des Tages (Wohnräume)")
ax.axvspan(U0,U1,color=GRAU,alpha=.25); ax.axvline(INST,color="k",ls="--",lw=1.5)
def note(x,y,t,xt,yt): ax.annotate(t,(pd.Timestamp(x),y),xytext=(pd.Timestamp(xt),yt),fontsize=11.5,ha="center",arrowprops=dict(arrowstyle="->",color="k"),bbox=dict(boxstyle="round",fc="white",ec=GRAU,alpha=.95))
note("2026-03-25",230,"Anfang: sehr hohe Werte\n(Problem entdeckt, dann gelüftet)","2026-04-20",370)
note("2026-08-03",340,"Urlaub: Haus 6 Tage zu\n→ Radon steigt in allen Räumen","2026-07-02",400)
note("2026-07-20",150,"20.07.: wahrscheinlich\nFenster zu","2026-06-12",250)
note("2026-08-24",120,"24.08.: Überdruck-Anlage\neingebaut","2026-09-22",300)
ax.set_ylabel("Radon in Bq/m³ (Zerfälle pro Sekunde je m³ Luft)"); ax.set_title("Radon in den Wohnräumen: fast immer im grünen Bereich")
ax.legend(loc="upper left",fontsize=11,frameon=False); fig.tight_layout(); fig.savefig("bilder/e1_gesamtverlauf.png",dpi=100); plt.close()
# ---------- Bild 2: typischer Tag vor/nach
ok=OG.copy(); ok[(ok.index>=U0)&(ok.index<U1)]=np.nan; ok=ok[ok.index>="2026-04-01"]
pre=ok[ok.index<INST].dropna(); post=ok[ok.index>=INST].dropna()
def prof(s): g=s.groupby(s.index.hour); return g.median(),g.quantile(.25),g.quantile(.75)
(pm,p1,p3),(qm,q1,q3)=prof(pre),prof(post)
fig,ax=plt.subplots(figsize=(11,5.5)); hr=np.arange(24)
ax.fill_between(hr,p1,p3,color=ORANGE,alpha=.18); ax.fill_between(hr,q1,q3,color=BLAU,alpha=.18)
ax.plot(hr,pm,color=ORANGE,lw=2.6,label="vor der Anlage (01.04.–23.08., ohne Urlaub)"); ax.plot(hr,qm,color=BLAU,lw=2.6,label="nach der Anlage (ab 24.08.)")
ax.set_xticks(range(0,24,3)); ax.set_xticklabels([f"{i}:00" for i in range(0,24,3)]); ax.set_xlabel("Uhrzeit"); ax.set_ylabel("Radon in Bq/m³"); ax.set_ylim(0,None)
ax.set_title("Ein typischer Tag: nachts höher, tagsüber niedriger"); ax.legend(frameon=False,loc="upper right"); ax.text(0.01,0.02,"Linie = Mitte, Fläche = die mittleren 50 % aller Tage",transform=ax.transAxes,fontsize=10.5,color=GRAU)
fig.tight_layout(); fig.savefig("bilder/e2_typischer_tag.png",dpi=100); plt.close()
night=lambda m:m.loc[2:7].mean(); day=lambda m:m.loc[12:17].mean()
print("Typischer Tag Median: vor Nacht(02-07)",round(night(pm),1),"Tag(12-17)",round(day(pm),1),"| nach Nacht",round(night(qm),1),"Tag",round(day(qm),1))
print("P75 Nacht: vor",round(p3.loc[2:7].mean(),1),"nach",round(q3.loc[2:7].mean(),1))
# ---------- Bild 3: Wirkung (woechentlich)
v=pd.DataFrame({"OG":OG,"OGmax":OGmax,"Sock":h.KuecheSockel_Rn,"Kue":h.Kueche_Rn})
v=v[v.index>="2026-04-01"]; v.loc[(v.index>=U0)&(v.index<U1),:]=np.nan
v["exc"]=v.Sock-v.Kue; v["over100"]=(v.OGmax>100).astype(float).where(v.OGmax.notna())
wk=pd.DataFrame({"n":v.OGmax.resample("W-SUN").count(),"p100":100*v.over100.resample("W-SUN").mean(),"exc":v.exc.resample("W-SUN").median(),"OG":v.OG.resample("W-SUN").median()})
wk.loc[wk.n<84,["p100","exc","OG"]]=np.nan; wk.to_csv("analyse/wirkung_woche.csv")
print(wk.round(1).to_string())
fig,(a,b)=plt.subplots(2,1,figsize=(12,8),sharex=True)
cols=[BLAU if (t-pd.Timedelta(days=6))>=INST else ORANGE for t in wk.index]
a.bar(wk.index-pd.Timedelta(days=3),wk.p100,width=5.5,color=cols); a.axvline(INST,color="k",ls="--"); a.set_ylabel("Anteil Stunden über 100 Bq/m³ (%)")
[a.text(t-pd.Timedelta(days=3),.15,"0 %",ha="center",fontsize=10.5,color=BLAU) for t,pv in zip(wk.index,wk.p100) if pv==0 and (t-pd.Timedelta(days=6))>=INST]
a.set_title("1) Hohe Spitzen: vor der Anlage regelmäßig, danach praktisch nie"); a.text(INST+pd.Timedelta(days=2),a.get_ylim()[1]*.85,"Anlage eingebaut",fontsize=11)
b.plot(wk.index-pd.Timedelta(days=3),wk.exc,color=ORANGE,lw=2.4,marker="o"); b.axvline(INST,color="k",ls="--"); b.axhline(0,color=GRAU,lw=1); b.set_ylabel("Radon Sockel minus Küche-Mitte (Bq/m³)")
b.set_title("2) Eintritt von Bodenluft an der Außenwand: vor der Anlage deutlich, danach Null")
b.set_xlim(pd.Timestamp("2026-04-01"),pd.Timestamp("2026-10-14")); fig.tight_layout(); fig.savefig("bilder/e3_wirkung.png",dpi=100); plt.close()
# ---------- Bild 4: Urlaub einfach
x=h.loc["2026-07-28":"2026-08-09"]
fig,(a,b)=plt.subplots(2,1,figsize=(12,7),sharex=True,gridspec_kw={"height_ratios":[3,2]})
a.axvspan(U0,U1,color=GRAU,alpha=.2); b.axvspan(U0,U1,color=GRAU,alpha=.2)
a.plot(x.index,x[OGc].mean(axis=1),color=BLAU,lw=2.4); a.set_ylabel("Radon Wohnräume (Bq/m³)"); a.set_title("Urlaub: Haus zu → Radon steigt, nach der Rückkehr (Lüften) sofort weg")
a.axhline(300,color=ROT,ls=":"); a.text(x.index[3],310,"300 = österreichischer Referenzwert (gilt für das Jahresmittel)",fontsize=10.5,color=ROT)
b.plot(x.index,x["KuecheL_CO₂_(ppm)"],color=GRUEN,lw=2); b.set_ylabel("CO₂ Küche (ppm)"); b.text(U0+pd.Timedelta(hours=10),700,"CO₂ flach = niemand zuhause",fontsize=11)
fig.tight_layout(); fig.savefig("bilder/e4_urlaub.png",dpi=100); plt.close()
# ---------- Kennzahlen Wirkung (fuer Text)
pre=ok[ok.index<INST].dropna(); post=ok[ok.index>=INST].dropna()
print("\nMittel OG vor/nach:",round(pre.mean(),1),round(post.mean(),1),"| Stunden >60:",round(100*(pre>60).mean(),1),round(100*(post>60).mean(),1),"| Mittel ohne >60:",round(pre[pre<=60].mean(),1),round(post[post<=60].mean(),1))
m=OGmax[(OGmax.index>="2026-04-01")]; m=m[~((m.index>=U0)&(m.index<U1))]
print("Stunden Wohnraum>100: vor",int((m[m.index<INST]>100).sum()),"von",int(m[m.index<INST].count()),"nach",int((m[m.index>=INST]>100).sum()),"von",int(m[m.index>=INST].count()))
print("Vor Einbau Mittel inkl. Urlaub (ganze Zeit ab 01.04.):",round(OG[(OG.index>='2026-04-01')&(OG.index<INST)].mean(),1))
print("Hoechster Stundenwert OG-Mittel nach Einbau:",round(OG[OG.index>=INST].max(),0),OG[OG.index>=INST].idxmax(),"| Einzelraum max:",round(OGmax[OGmax.index>=INST].max(),0))
sock=v.exc; print("Sockel-Ueberschuss Median vor/nach:",round(sock[sock.index<INST].median(),1),round(sock[sock.index>=INST].median(),1))
