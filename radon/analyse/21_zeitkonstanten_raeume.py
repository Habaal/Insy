"""Warum unterscheiden sich die Zeitkonstanten der Räume? Anstieg, Abfall beim Lüften, Verzögerung."""
from common import *
from scipy.optimize import curve_fit
df=laden(); df.columns=[kurz(c).replace("Schlaf_Radon_(Bq/m³)","Schlaf_Rn") for c in df.columns]
R={"Wohnzimmer":"Wohnzimmer_Rn","Küche":"Kueche_Rn","Büro":"Buero_Rn","Schlafzimmer":"Schlaf_Rn","Küche Sockel":"KuecheSockel_Rn"}
U0=pd.Timestamp("2026-07-31 18:00")
h=df[list(R.values())].resample("h").mean(); m10=df[list(R.values())].resample("10min").mean()
def charge(t,css,c0,tau): return css-(css-c0)*np.exp(-t/tau)
def charge_d(t,css,c0,tau,d): tt=np.clip(t-d,0,None); return css-(css-c0)*np.exp(-tt/tau)
def expo(t,c,a,lam): return c+a*np.exp(-lam*t)
rows=[]
for nm,c in R.items():
    x=h[c].loc[U0:"2026-08-06 18:00"].dropna(); t=(x.index-U0).total_seconds().values/3600
    p,_=curve_fit(charge,t,x.values,p0=[350,70,30],maxfev=20000)
    pd_,_=curve_fit(charge_d,t,x.values,p0=[350,70,30,3],bounds=([0,0,1,0],[800,300,200,48]),maxfev=20000)
    # Zeit bis 50 % / 90 % des Anstiegs (geglaettet 6 h)
    xs=x.rolling(6,center=True,min_periods=3).mean(); lo,hi=xs.iloc[:6].mean(),xs.loc["2026-08-05":"2026-08-06 18:00"].mean()
    t50=(xs[xs>=lo+.5*(hi-lo)].index[0]-U0).total_seconds()/3600; t90=(xs[xs>=lo+.9*(hi-lo)].index[0]-U0).total_seconds()/3600
    # Abfall beim Lueften nach Rueckkehr
    y=m10[c].loc["2026-08-06 20:30":"2026-08-07 01:00"].dropna(); ty=(y.index-y.index[0]).total_seconds().values/3600
    q,_=curve_fit(expo,ty,y.values,p0=[15,300,1.3],bounds=([0,20,0.05],[60,800,10]),maxfev=20000)
    # Sprung: wann faellt der Raum unter 50 % seines Urlaubsniveaus?
    lev=m10[c].loc["2026-08-06 12:00":"2026-08-06 19:00"].mean(); yy=m10[c].loc["2026-08-06 19:00":"2026-08-07 06:00"]
    tdrop=yy[yy<lev*.5].index[0].strftime("%H:%M") if (yy<lev*.5).any() else "-"
    rows.append(dict(Raum=nm,tau=round(p[2],1),Css=round(p[0]),tau_mit_Verzoegerung=round(pd_[2],1),Verzoegerung_h=round(pd_[3],1),t50_h=round(t50),t90_h=round(t90),Abfall_pro_h=round(q[2],2),unter_50pct_um=tdrop))
print(pd.DataFrame(rows).to_string(index=False))
# Rohdaten-Granularitaet: Schrittweite der Messwerte und Wiederholungen (Hinweis auf internes Mittel)
for nm,c in R.items():
    s=df[c].dropna(); s=s[~s.index.duplicated()]; dt=s.index.to_series().diff().dt.total_seconds().median()/60
    same=(s.diff()==0).mean()
    print(f"{nm:13s} Intervall {dt:.0f} min, Anteil unveränderter Folgewerte {100*same:.0f} %")
