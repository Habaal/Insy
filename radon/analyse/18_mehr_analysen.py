"""Zusatzanalysen: Wetter, Luftqualitaet, Luftwechsel, Sensorrauschen, Grenzwert-Zeiten.
Schreibt befunde_daten.js (fuer die interaktive Befunde-Seite) und druckt die Kennzahlen."""
from common import *
import json
from scipy.optimize import curve_fit

df = laden()
df.columns = [kurz(c).replace("Schlaf_Radon_(Bq/m³)", "Schlaf_Rn") for c in df.columns]
h = df.resample("h").mean()
ROOMS = [("wohn", "Wohnzimmer", "Wohnzimmer_Rn"), ("kueche", "Küche", "Kueche_Rn"), ("buero", "Büro", "Buero_Rn"), ("schlaf", "Schlafzimmer", "Schlaf_Rn"),
         ("sockel", "Küche Sockel", "KuecheSockel_Rn"), ("technik", "Technikraum", "Technikraum_Rn"), ("werk", "Werkstatt", "Werkstatt_Rn")]
R = pd.DataFrame({k: h[c] for k, _, c in ROOMS})
OGk = ["wohn", "kueche", "buero", "schlaf"]
OG = R[OGk].mean(axis=1)
INST = pd.Timestamp("2026-08-24"); U0, U1 = pd.Timestamp("2026-07-31 18:00"), pd.Timestamp("2026-08-06 19:30")
Tout, P, Wind, S54 = h["W_Temperatur_2_m_(°C)"], h["W_Luftdruck_(hPa)"], h["W_Wind_10_m_(km/h)"], h["W_Bodentemperatur_54_cm_(°C)"]
Tin = h[["KuecheL_Temperatur_innen_(°C)", "Schlaf_Temperatur_innen_(°C)"]].mean(axis=1)
CO2K, CO2S = h["KuecheL_CO₂_(ppm)"], h["Schlaf_CO₂_(ppm)"]
RHK, RHS = h["KuecheL_rel._Luftfeuchte_(%)"], h["Schlaf_rel._Luftfeuchte_(%)"]
urlaub = (h.index >= U0) & (h.index < U1)
out = {}

# ---------------------------------------------------------------- A) Wetter (Nachtwerte je Tag)
rows = []
for d in pd.date_range("2026-04-01", "2026-10-12"):
    a, b = d + pd.Timedelta(hours=2), d + pd.Timedelta(hours=6)
    seg = slice(a, b)
    if urlaub[(h.index >= a) & (h.index <= b)].any():
        continue
    og = OG.loc[seg].mean()
    if np.isnan(og):
        continue
    w = slice(d, b)
    rows.append(dict(d=d.strftime("%Y-%m-%d"), og=og, wind=Wind.loc[w].mean(), dT=(Tin.loc[seg] - Tout.loc[seg]).mean(), tout=Tout.loc[seg].mean(),
                     dp12=P.loc[b] - P.loc[b - pd.Timedelta(hours=12)] if b in P.index and (b - pd.Timedelta(hours=12)) in P.index else np.nan,
                     soil=S54.loc[seg].mean(), post=int(d >= INST)))
W = pd.DataFrame(rows)
W["lg"] = np.log1p(W.og)
feat = ["wind", "dT", "tout", "dp12", "soil"]
print("Nächte:", len(W), "(vor", int((W.post == 0).sum()), "nach", int((W.post == 1).sum()), ")")
cor = {}
for nm, sub in [("alle", W), ("vor", W[W.post == 0]), ("nach", W[W.post == 1])]:
    cor[nm] = {f: (None if sub[f].notna().sum() < 15 else round(float(sub[["lg", f]].dropna().corr(method="spearman").iloc[0, 1]), 2)) for f in feat}
print(pd.DataFrame(cor).to_string())
# Regression (standardisiert), Bootstrap
Z = W.dropna(subset=["lg", "wind", "dT", "dp12"]).copy()
X = pd.DataFrame({"Wind": Z.wind, "Innen-Außen-Temp.": Z.dT, "Druckänderung 12 h": Z.dp12, "nach Anlage": Z.post.astype(float)})
Xs = (X - X.mean()) / X.std(); Xs.loc[:, "nach Anlage"] = X["nach Anlage"]
A = np.column_stack([np.ones(len(Xs)), Xs.values]); y = Z.lg.values
beta = np.linalg.lstsq(A, y, rcond=None)[0]; res = y - A @ beta; r2 = 1 - res.var() / y.var()
rng = np.random.default_rng(1); bs = []
for _ in range(800):
    ix = rng.integers(0, len(y), len(y)); bs.append(np.linalg.lstsq(A[ix], y[ix], rcond=None)[0])
bs = np.array(bs); ci = np.percentile(bs, [2.5, 97.5], axis=0)
reg = [dict(name=n, b=round(float(beta[i + 1]), 3), lo=round(float(ci[0, i + 1]), 3), hi=round(float(ci[1, i + 1]), 3)) for i, n in enumerate(Xs.columns)]
print("Regression log(Radon nachts) R2=%.2f n=%d" % (r2, len(y))); print(pd.DataFrame(reg).to_string())
W["bin"] = pd.cut(W.tout, [-5, 6, 9, 12, 15, 18, 21, 30]); W["bin"] = W["bin"].astype(str)
gb = []
for b_, g in W.groupby("bin", sort=False):
    a_, c_ = g[g.post == 0].og, g[g.post == 1].og
    gb.append(dict(bin=b_, n0=int(len(a_)), n1=int(len(c_)), m0=None if not len(a_) else round(float(a_.median()), 1), m1=None if not len(c_) else round(float(c_.median()), 1)))
gb = sorted(gb, key=lambda r: float(r["bin"].strip("()[]").split(",")[0]))
m_ = W[(W.tout >= 6) & (W.tout < 15)]
match = dict(vor=round(float(m_[m_.post == 0].og.median()), 1), nach=round(float(m_[m_.post == 1].og.median()), 1), n0=int((m_.post == 0).sum()), n1=int((m_.post == 1).sum()),
             gt60_vor=round(100 * float((m_[m_.post == 0].og > 60).mean()), 1), gt60_nach=round(100 * float((m_[m_.post == 1].og > 60).mean()), 1))
print("gleiche Außentemperatur 6-15 °C:", match)
out["wetter"] = dict(bins=gb, match=match, tage=[{k: (None if (isinstance(v, float) and np.isnan(v)) else (round(v, 2) if isinstance(v, float) else v)) for k, v in r.items() if k != "lg"} for r in W.to_dict("records")],
                     cor=cor, reg=reg, r2=round(float(r2), 2), n=int(len(y)))

# ---------------------------------------------------------------- B) Luftqualitaet
mon = {5: "Mai", 6: "Juni", 7: "Juli", 8: "August", 9: "September", 10: "Oktober"}
lq = []
for m, nm in mon.items():
    sel = h.index.month == m
    row = dict(monat=nm)
    for key, s in [("K", CO2K), ("S", CO2S)]:
        v = s[sel].dropna()
        row[f"co2_{key}_n"] = int(len(v)); row[f"co2_{key}_gt1000"] = round(100 * (v > 1000).mean(), 1) if len(v) else None
        row[f"co2_{key}_gt1400"] = round(100 * (v > 1400).mean(), 1) if len(v) else None
        row[f"co2_{key}_max"] = int(v.max()) if len(v) else None
    for key, s in [("K", h["KuecheL_Temperatur_innen_(°C)"]), ("S", h["Schlaf_Temperatur_innen_(°C)"])]:
        v = s[sel].dropna(); row[f"t_{key}_gt26"] = round(100 * (v > 26).mean(), 1) if len(v) else None; row[f"t_{key}_mean"] = round(float(v.mean()), 1) if len(v) else None
    for key, s in [("K", RHK), ("S", RHS)]:
        v = s[sel].dropna(); row[f"rh_{key}_gt70"] = round(100 * (v > 70).mean(), 1) if len(v) else None; row[f"rh_{key}_gt60"] = round(100 * (v > 60).mean(), 1) if len(v) else None; row[f"rh_{key}_mean"] = round(float(v.mean()), 1) if len(v) else None
    lq.append(row)
print(pd.DataFrame(lq).T.to_string())
# Nacht-CO2 Schlafzimmer (23-06 Uhr Mittel je Nacht)
nc = []
for d in pd.date_range("2026-05-14", "2026-10-12"):
    s = CO2S.loc[d + pd.Timedelta(hours=23): d + pd.Timedelta(hours=30)]
    if s.notna().sum() >= 5 and not urlaub[(h.index >= d + pd.Timedelta(hours=23)) & (h.index <= d + pd.Timedelta(hours=30))].any():
        nc.append((d, s.mean()))
nc = pd.Series(dict(nc))
print("Nächte Schlafzimmer-CO2 (23-06 Uhr): n=%d, Median %.0f, >1000: %.0f%%, >1400: %.0f%%" % (len(nc), nc.median(), 100 * (nc > 1000).mean(), 100 * (nc > 1400).mean()))
out["luft"] = dict(monate=lq, nacht=dict(n=int(len(nc)), med=round(float(nc.median())), gt1000=round(100 * float((nc > 1000).mean()), 1), gt1400=round(100 * float((nc > 1400).mean()), 1)))
# Wochentag/Wochenende: CO2 Kueche + Radon Wohnbereich nach Uhrzeit
wd = h.index.dayofweek < 5
prof = {}
for nm, sel in [("werktag", wd), ("wochenende", ~wd)]:
    m = ~urlaub & sel
    prof[nm] = dict(co2=[None if np.isnan(x) else round(float(x)) for x in CO2K[m].groupby(h.index[m].hour).median().reindex(range(24))],
                    rn=[round(float(x), 1) for x in OG[m & (h.index >= "2026-04-01")].groupby(h.index[m & (h.index >= "2026-04-01")].hour).median().reindex(range(24))])
out["wochentag"] = prof
print("Werktag/Wochenende Radon Wohnbereich Median Tag gesamt:", round(float(OG[~urlaub & wd].median()), 1), round(float(OG[~urlaub & ~wd].median()), 1))

# ---------------------------------------------------------------- C) Luftwechsel (grobe Schaetzung, Einzonenmodell)
def expo(t, c0, a, lam): return c0 + a * np.exp(-lam * t)
vent = {}
for nm, s in [("Küche", CO2K), ("Schlafzimmer", CO2S)]:
    x = s.loc["2026-08-01 00:00":"2026-08-05 12:00"].dropna(); t = (x.index - x.index[0]).total_seconds().values / 3600
    p, _ = curve_fit(expo, t, x.values, p0=[405, 150, 0.05], maxfev=20000)
    vent[nm] = dict(cout=round(float(p[0])), lam=round(float(p[2]), 3)); print("CO2-Abfall Urlaub", nm, "Aussen~%.0f ppm, Luftwechsel %.3f/h (Halbwertszeit %.0f h)" % (p[0], p[2], np.log(2) / p[2]))
ach = float(np.mean([v["lam"] for v in vent.values()]))
xr = OG.loc["2026-07-31 18:00":"2026-08-06 18:00"].dropna(); t = (xr.index - xr.index[0]).total_seconds().values / 3600
def rise(t, css, c0, L): return css - (css - c0) * np.exp(-L * t)
pr, _ = curve_fit(rise, t, xr.values, p0=[350, 70, 0.02], maxfev=20000)
LAM_RN = np.log(2) / (3.82 * 24)
print("Radon-Anstieg Urlaub: Sättigung %.0f Bq/m3, Gesamt-Verlustrate %.3f/h (Luftwechsel aus CO2 %.3f + Zerfall %.4f)" % (pr[0], pr[2], ach, LAM_RN))
S_urlaub = float(pr[0] * pr[2])
print("Radon-Quellstärke im geschlossenen Haus ~ %.0f Bq/m3 pro Stunde (aus Sättigung x Verlustrate), %.0f (aus Sättigung x (Luftwechsel+Zerfall))" % (S_urlaub, pr[0] * (ach + LAM_RN)))
o10 = df[OGk[0] + "_x"] if False else None
og10 = df[["Buero_Rn", "Kueche_Rn", "Wohnzimmer_Rn", "Schlaf_Rn"]].resample("10min").mean().mean(axis=1)
xe = og10.loc["2026-08-06 20:50":"2026-08-07 00:30"].dropna(); t = (xe.index - xe.index[0]).total_seconds().values / 3600
pe, _ = curve_fit(expo, t, xe.values, p0=[12, 220, 1.3], bounds=([0, 50, 0.1], [40, 600, 6]), maxfev=20000)
print("Lüften nach Rückkehr: Radon fällt auf %.0f Bq/m3, Luftwechsel ~%.1f /h (Halbwertszeit %.0f min)" % (pe[0], pe[2], 60 * np.log(2) / pe[2]))
sv = h.loc["2026-07-29":"2026-08-09"]
out["luftwechsel"] = dict(co2=vent, ach_urlaub=round(ach, 3), sat=round(float(pr[0])), Lges=round(float(pr[2]), 3), S=round(float(pr[0] * (ach + LAM_RN)), 1), ach_lueften=round(float(pe[2]), 2),
                          basis_nach=round(float(pe[0])), t0=sv.index[0].strftime("%Y-%m-%d %H:%M"),
                          rn=[None if np.isnan(x) else round(float(x), 1) for x in OG.loc[sv.index]], co2k=[None if np.isnan(x) else round(float(x)) for x in CO2K.loc[sv.index]],
                          co2s=[None if np.isnan(x) else round(float(x)) for x in CO2S.loc[sv.index]])

# ---------------------------------------------------------------- D) Sensorrauschen
n_ = {}
for a_, b_ in [("buero", "wohn"), ("buero", "kueche"), ("kueche", "wohn")]:
    d_ = (R[a_] - R[b_]).dropna(); lvl = (R[a_] + R[b_]) / 2
    for nm, m in [("unter 50", lvl < 50), ("50-150", (lvl >= 50) & (lvl < 150)), ("ueber 150", lvl >= 150)]:
        x = d_[m.reindex(d_.index, fill_value=False)]
        n_[f"{a_}-{b_} {nm}"] = (round(float(1.4826 * np.median(np.abs(x - x.median()))), 1), int(len(x)))
print("Sensor-zu-Sensor-Streuung (robuste SD der Stundendifferenz, Bq/m3):"); [print(" ", k, v) for k, v in n_.items()]
allsd = {nm: np.mean([n_[f"{p}-{q} {nm}"][0] for p, q in [("buero", "wohn"), ("buero", "kueche"), ("kueche", "wohn")]]) for nm in ["unter 50", "50-150", "ueber 150"]}
print("Mittel:", {k: round(v, 1) for k, v in allsd.items()})
out["rauschen"] = {k: round(float(v), 1) for k, v in allsd.items()}
# Herbst-Anstieg vs Aussentemperatur (Wochenmediane)
wk = pd.DataFrame({"og": OG[~urlaub].resample("W").median(), "tout": Tout.resample("W").mean()}).loc["2026-08-30":"2026-10-11"]
print("Herbst: Wochenmedian OG vs. Außentemperatur:\n", wk.round(1).to_string(), "\nSpearman:", round(float(wk.corr(method='spearman').iloc[0, 1]), 2))
out["herbst"] = [dict(w=i.strftime("%Y-%m-%d"), og=round(float(r.og), 1), tout=round(float(r.tout), 1)) for i, r in wk.iterrows()]

# ---------------------------------------------------------------- E) Grenzwert-Zeiten je Raum und Phase
per = {"vor": (R.index >= "2026-04-01") & (R.index < INST) & ~urlaub, "urlaub": urlaub & (R.index >= "2026-08-01"), "nach": (R.index >= INST)}
tab = []
for k, nm, _ in ROOMS:
    row = dict(raum=nm, k=k)
    for p, m in per.items():
        v = R.loc[m, k].dropna()
        row[p] = dict(n=int(len(v)), mean=round(float(v.mean()), 1), p95=round(float(v.quantile(.95)), 0), max=int(v.max()), gt100=round(100 * float((v > 100).mean()), 1), gt300=round(100 * float((v > 300).mean()), 1))
    tab.append(row)
print(pd.DataFrame([{**{"raum": r["raum"]}, **{f"{p}_{q}": r[p][q] for p in per for q in ["mean", "gt100", "gt300"]}} for r in tab]).to_string())
out["grenz"] = tab

# ---------------------------------------------------------------- F) Nachtanstieg
sl = []
for d in pd.date_range("2026-04-01", "2026-10-12"):
    a, b = d + pd.Timedelta(hours=22), d + pd.Timedelta(hours=29)
    if a in OG.index and b in OG.index and not np.isnan(OG[a]) and not np.isnan(OG[b]) and not urlaub[(h.index >= a) & (h.index <= b)].any():
        sl.append((d, (OG[b] - OG[a]) / 7))
sl = pd.Series(dict(sl)); pre, post = sl[sl.index < INST], sl[sl.index >= INST]
print("Nachtanstieg (22->05 Uhr, Bq/m3 pro h): vor Median %.1f (P75 %.1f), nach Median %.1f (P75 %.1f); Nächte %d / %d" % (pre.median(), pre.quantile(.75), post.median(), post.quantile(.75), len(pre), len(post)))
out["nacht"] = dict(vor=[round(float(pre.median()), 2), round(float(pre.quantile(.75)), 2), int(len(pre))], nach=[round(float(post.median()), 2), round(float(post.quantile(.75)), 2), int(len(post))])

# ---------------------------------------------------------------- G) Kennzahlen fuer Dosisrechner
m_pre = (OG.index >= "2026-04-01") & (OG.index < INST) & ~urlaub; m_post = OG.index >= INST
out["mittel"] = dict(vor=round(float(OG[m_pre].mean()), 1), nach=round(float(OG[m_post].mean()), 1), urlaub=round(float(OG[urlaub & (OG.index >= "2026-08-01")].mean())))
print("Mittel Wohnräume vor/nach/Urlaub:", out["mittel"])
# Raum-Ranking
print("Raum-Mittel (ohne Urlaub, ab 01.04.):", {k: round(float(R.loc[(R.index >= '2026-04-01') & ~urlaub, k].mean()), 1) for k, _, _ in ROOMS})

# ---------------------------------------------------------------- H) Tageswerte und Ereignisse fuer die Befunde-Seite
dd = pd.DataFrame({"og": OG.resample("D").median(), "ogmax": R[OGk].max(axis=1).resample("D").max(), "sock": R["sockel"].resample("D").median(), "tech": R["technik"].resample("D").median()})
def _r(x):
    return None if pd.isna(x) else round(float(x), 0)
out["tage"] = dict(d=[i.strftime("%Y-%m-%d") for i in dd.index], og=[_r(x) for x in dd.og], ogmax=[_r(x) for x in dd.ogmax], sock=[_r(x) for x in dd.sock], tech=[_r(x) for x in dd.tech])
NOTIZEN = {
    "2026-03-28 02": "Anfang der Messung: Problem entdeckt, dann etwas dagegen unternommen",
    "2026-03-30 15": "kurz nach Sensorstart Küche-Sockel (13:50), Einlaufphase",
    "2026-07-11 23": "kurze Spitze; laut Hr. Grimmer vielleicht Messungenauigkeit. Davor Schlafzimmer-CO₂ 1767 ppm",
    "2026-07-16 12": "nur im Keller (laut Hr. Grimmer weniger wichtig)",
    "2026-07-20 11": "tagsüber alle Wohnräume hoch; laut Hr. Grimmer wahrscheinlich Fenster zu",
    "2026-08-11 20": "kurze Spitze; laut Hr. Grimmer vielleicht Messungenauigkeit. Schlafzimmer-CO₂ ~1050",
    "2026-08-23 01": "nachts, einen Tag vor dem Einbau; laut Hr. Grimmer nichts Besonderes, Ursache unbekannt",
    "2026-10-11 01": "Küche-CO₂ erreicht am selben Tag den Höchstwert (1778 ppm)",
}
ev = pd.read_csv("analyse/ereignisse_radon.csv", parse_dates=["von", "bis"])
evl = []
for r in ev.itertuples():
    evl.append(dict(art="Radon-Ereignis", von=r.von.strftime("%Y-%m-%d %H:%M"), bis=r.bis.strftime("%Y-%m-%d %H:%M"),
                    raeume=r.Raeume.replace(",", ", ").replace("KuecheSockel", "Küche Sockel").replace("Kueche", "Küche").replace("Buero", "Büro").replace("Schlaf", "Schlafzimmer"),
                    peak=int(r.Peak), notiz=NOTIZEN.get(r.von.strftime("%Y-%m-%d %H"), "")))
for t in ["2026-04-16 07:00", "2026-04-30 16:00", "2026-07-06 06:00", "2026-08-30 11:00", "2026-09-10 14:00", "2026-09-16 15:00"]:
    evl.append(dict(art="Sensor-Reset", von=t, bis=t, raeume="alle Sensoren", peak=None, notiz="Betriebszeit aller Sensoren springt auf 0; Ursache laut Hr. Grimmer unbekannt"))
evl.append(dict(art="Phase", von="2026-07-31 18:00", bis="2026-08-06 19:30", raeume="", peak=None, notiz="Urlaub (von Hr. Grimmer bestätigt)"))
evl.append(dict(art="Phase", von="2026-04-01 00:00", bis="2026-06-17 23:59", raeume="", peak=None, notiz="überwiegend gelüftet (sporadisch, laut Hr. Grimmer)"))
evl.append(dict(art="Wendepunkt", von="2026-08-24 00:00", bis="2026-08-24 00:00", raeume="", peak=None, notiz="Überdruck-Anlage eingebaut (bestätigt)"))
out["ereignisse"] = sorted(evl, key=lambda e: e["von"])

js = "const BEF = " + json.dumps(out, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + ";\n"
open("befunde_daten.js", "w", encoding="utf-8").write(js)
print("befunde_daten.js", round(len(js) / 1024), "KB")
