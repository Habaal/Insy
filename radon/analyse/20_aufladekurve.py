"""Radon-Aufladekurve im Urlaub (Kondensator-Analogie): Zeitkonstante, Quellstaerke, Druck (Kamineffekt), Anlagen-Aequivalent.
Ergaenzt befunde_daten.js um den Block 'modell'."""
from common import *
import json
from scipy.optimize import curve_fit

df = laden()
df.columns = [kurz(c).replace("Schlaf_Radon_(Bq/m³)", "Schlaf_Rn") for c in df.columns]
h = df.resample("h").mean()
OGc = ["Buero_Rn", "Kueche_Rn", "Wohnzimmer_Rn", "Schlaf_Rn"]
LAM = np.log(2) / (3.82 * 24)  # Radon-222 Zerfall pro Stunde (Halbwertszeit 3,82 d, Allgemeinwissen)
U0, U1 = pd.Timestamp("2026-07-31 18:00"), pd.Timestamp("2026-08-06 19:30")
INST = pd.Timestamp("2026-08-24")

# ---------- 1) Aufladekurve: C(t) = Css - (Css - C0) * exp(-t/tau)
def charge(t, css, c0, tau): return css - (css - c0) * np.exp(-t / tau)
res = {}
for nm, cols in [("Wohnbereich (Mittel)", OGc), ("Wohnzimmer", ["Wohnzimmer_Rn"]), ("Küche", ["Kueche_Rn"]), ("Büro", ["Buero_Rn"]), ("Schlafzimmer", ["Schlaf_Rn"])]:
    x = h[cols].mean(axis=1).loc[U0:U1 - pd.Timedelta(hours=1)].dropna(); t = (x.index - U0).total_seconds().values / 3600
    p, cov = curve_fit(charge, t, x.values, p0=[350, 70, 30], maxfev=20000)
    se = np.sqrt(np.diag(cov)); fitv = charge(t, *p); r2 = 1 - ((x.values - fitv) ** 2).sum() / ((x.values - x.values.mean()) ** 2).sum()
    res[nm] = dict(css=p[0], c0=p[1], tau=p[2], se_css=se[0], se_tau=se[2], r2=r2, S=p[0] / p[2])
    print(f"{nm:22s} Css={p[0]:.0f}±{se[0]:.0f}  C0={p[1]:.0f}  tau={p[2]:.1f}±{se[2]:.1f} h  R2={r2:.3f}  S=Css/tau={p[0]/p[2]:.1f} Bq/m3/h")
m = res["Wohnbereich (Mittel)"]
Ltot = 1 / m["tau"]; ACH_fit = Ltot - LAM
print(f"Gesamt-Verlustrate {Ltot:.4f}/h -> Luftwechsel (ohne Zerfall) {ACH_fit:.4f}/h, Zerfall {LAM:.4f}/h")

# ---------- 2) Unabhaengiger Luftwechsel aus CO2 (Abfall im leeren Haus)
def expo(t, c, a, lam): return c + a * np.exp(-lam * t)
ach_co2 = {}
for nm, col in [("Küche", "KuecheL_CO₂_(ppm)"), ("Schlafzimmer", "Schlaf_CO₂_(ppm)")]:
    s = h[col].loc["2026-08-01 00:00":"2026-08-05 12:00"].dropna(); t = (s.index - s.index[0]).total_seconds().values / 3600
    p, cov = curve_fit(expo, t, s.values, p0=[405, 150, .05], maxfev=20000); ach_co2[nm] = (p[2], np.sqrt(cov[2, 2]))
    print(f"CO2 {nm}: Luftwechsel {p[2]:.3f} ± {np.sqrt(cov[2,2]):.3f} /h (Außenluft-Niveau {p[0]:.0f} ppm)")
ach_c = float(np.mean([v[0] for v in ach_co2.values()]))
S_co2 = m["css"] * (ach_c + LAM)
print(f"Quellstärke aus CO2-Luftwechsel: {S_co2:.1f} Bq/m3/h | aus Aufladekurve: {m['S']:.1f} Bq/m3/h")

# ---------- 3) Druck durch Kamineffekt (aus gemessenen Temperaturen)
P0 = h["W_Luftdruck_(hPa)"] * 100
Tin = h[["KuecheL_Temperatur_innen_(°C)", "Schlaf_Temperatur_innen_(°C)"]].mean(axis=1) + 273.15
Tout = h["W_Temperatur_2_m_(°C)"] + 273.15
R_ = 287.05; G = 9.81
def dp_stack(hh): return (P0 / R_) * (1 / Tout - 1 / Tin) * G * hh   # Pa, positiv = Sog unten (Haus waermer als aussen)
for hh in (2.5, 3.0, 4.0): print(f"Kamineffekt Δp bei Höhe {hh} m ab Neutralzone: Median {dp_stack(hh).median():.2f} Pa, 95%-Wert {dp_stack(hh).quantile(.95):.2f} Pa, Max {dp_stack(hh).max():.2f}")
dpU = dp_stack(3.0).loc["2026-08-02":"2026-08-05"].mean(); dpN = dp_stack(3.0)[(dp_stack(3.0).index >= INST) & (dp_stack(3.0).index.hour < 7)].mean(); print(f"Δp(3 m) Urlaub {dpU:.2f} Pa; nachts nach 24.08.: {dpN:.2f} Pa")

# ---------- 4) Anlagen-Aequivalent: horizontale Verschiebung der Radon-ΔT-Kennlinie
OG = h[OGc].mean(axis=1); Wind = h["W_Wind_10_m_(km/h)"]
rows = []
for d in pd.date_range("2026-05-14", "2026-10-12"):
    a, b = d + pd.Timedelta(hours=2), d + pd.Timedelta(hours=6)
    if ((h.index >= U0 - pd.Timedelta(hours=24)) & (h.index <= U1 + pd.Timedelta(hours=24)) & (h.index >= a) & (h.index <= b)).any(): continue
    rows.append(dict(d=d, og=OG.loc[a:b].mean(), dT=(Tin.loc[a:b] - Tout.loc[a:b]).mean(), wind=Wind.loc[a:b].mean(), post=float(d >= INST), dp=dp_stack(3.0).loc[a:b].mean()))
W = pd.DataFrame(rows).dropna()
X = np.column_stack([np.ones(len(W)), W.dT, W.wind, W.post]); y = W.og.values
beta = np.linalg.lstsq(X, y, rcond=None)[0]
rng = np.random.default_rng(3); bs = []
for _ in range(1000):
    ix = rng.integers(0, len(y), len(y)); bb = np.linalg.lstsq(X[ix], y[ix], rcond=None)[0]; bs.append([bb[1], bb[3], -bb[3] / bb[1] if abs(bb[1]) > 1e-6 else np.nan])
bs = np.array(bs); ci = lambda a: tuple(np.nanpercentile(a, [2.5, 97.5]).round(2))
shiftK = -beta[3] / beta[1]
print(f"Nächte {len(W)}: Radon nachts = {beta[0]:.1f} + {beta[1]:.2f}·ΔT {beta[2]:+.2f}·Wind {beta[3]:+.1f}·nach_Anlage")
print(f"  ΔT-Koeffizient {beta[1]:.2f} Bq/m3 pro K (95 % {ci(bs[:,0])}), Anlage {beta[3]:.1f} Bq/m3 (95 % {ci(bs[:,1])})")
print(f"  Anlage entspricht einer ΔT-Verschiebung von {shiftK:.1f} K (95 % {ci(bs[:,2])})")
# Kamineffekt-Druck pro Kelvin Temperaturunterschied bei 3 m: d(Δp)/d(ΔT) ≈ rho*g*h/T  (rho = P/(R*T))
dpdT = float(np.nanmedian((P0 / (R_ * Tin) * G * 3.0 / Tin).dropna()))
dpA = shiftK * dpdT
dpA_ci = tuple(np.nanpercentile(bs[:, 2], [2.5, 97.5]) * dpdT)
print(f"  Pa pro K (3 m): {dpdT:.3f}; Überdruck-Äquivalent der Anlage: {dpA:.2f} Pa (95 % {dpA_ci[0]:.2f} bis {dpA_ci[1]:.2f})")

# ---------- 5) Export
dp3 = dp_stack(3.0)
out = json.loads(open("befunde_daten.js", encoding="utf-8").read()[len("const BEF = "):].rstrip(";\n"))
out["modell"] = dict(
    css=round(float(m["css"])), se_css=round(float(m["se_css"])), tau=round(float(m["tau"]), 1), se_tau=round(float(m["se_tau"]), 1), r2=round(float(m["r2"]), 3), c0=round(float(m["c0"])),
    S_fit=round(float(m["S"]), 1), S_co2=round(float(S_co2), 1), ach_fit=round(float(ACH_fit), 4), ach_co2=round(ach_c, 4), lam=round(float(LAM), 5),
    zimmer={k: dict(css=round(float(v["css"])), tau=round(float(v["tau"]), 1), r2=round(float(v["r2"]), 3)) for k, v in res.items()},
    dp=dict(h3_med=round(float(dp3.median()), 2), h3_p95=round(float(dp3.quantile(.95)), 2), urlaub=round(float(dpU), 2), nacht_nach=round(float(dpN), 2), paK=round(float(dpdT), 3)),
    anlage=dict(dT_koef=round(float(beta[1]), 2), dT_ci=ci(bs[:, 0]), anlage_bq=round(float(beta[3]), 1), anlage_ci=ci(bs[:, 1]), shift_K=round(float(shiftK), 1), shift_ci=ci(bs[:, 2]), dp_aeq=round(float(dpA), 2), dp_ci=[round(float(v), 2) for v in dpA_ci], n=int(len(W))),
    nacht=[dict(d=r.d.strftime("%Y-%m-%d"), og=round(float(r.og), 1), dp=round(float(r.dp), 2), post=int(r.post)) for r in W.itertuples()],
)
open("befunde_daten.js", "w", encoding="utf-8").write("const BEF = " + json.dumps(out, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + ";\n")
print("befunde_daten.js aktualisiert")
