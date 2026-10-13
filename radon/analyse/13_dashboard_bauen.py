"""Baut dashboard.html aus dashboard/template.html + Stundenwerten der CSV.
Aufruf (aus radon/): python -X utf8 analyse/13_dashboard_bauen.py
"""
from common import *
import json

df = laden()
df.columns = [kurz(c).replace("Schlaf_Radon_(Bq/m³)", "Schlaf_Rn") for c in df.columns]

RAEUME = [  # (Schluessel, Anzeigename, Spalte, Farbslot) - Farbe haengt am Raum, nicht am Rang
    ("wohn", "Wohnzimmer", "Wohnzimmer_Rn", 1),
    ("sockel", "Küche Sockel", "KuecheSockel_Rn", 2),
    ("technik", "Technikraum", "Technikraum_Rn", 3),
    ("werk", "Werkstatt", "Werkstatt_Rn", 4),
    ("buero", "Büro", "Buero_Rn", 5),
    ("kueche", "Küche", "Kueche_Rn", 6),
    ("schlaf", "Schlafzimmer", "Schlaf_Rn", 7),
]
MESS = {r[0]: r[2] for r in RAEUME}
MESS.update({"co2k": "KuecheL_CO₂_(ppm)", "co2s": "Schlaf_CO₂_(ppm)", "taus": "W_Temperatur_2_m_(°C)"})

idx = pd.date_range("2026-03-24 00:00", "2026-10-13 23:00", freq="h")
h = df[list(MESS.values())].resample("h").mean().reindex(idx)
h.columns = list(MESS.keys())


def liste(s, nd):
    return [None if pd.isna(v) else round(float(v), nd) for v in s]


serien = {k: liste(h[k], 1 if k == "taus" else 0) for k in h.columns}

# ---- Phasen (aus den Befunden; Hypothesen, von Hr. Grimmer zu bestaetigen)
PHASEN = [
    dict(id="fenster", name="Überwiegend gelüftet", von="2026-04-01 00:00", bis="2026-06-17 23:59",
         notiz="Laut Hr. Grimmer sporadisch, tendenziell mehr gelüftet als nicht (kein fester Zeitraum)"),
    dict(id="urlaub", name="Urlaub (Haus zu)", von="2026-07-31 18:00", bis="2026-08-06 19:30",
         notiz="Von Hr. Grimmer bestätigt: niemand zuhause, alles geschlossen"),
]
WENDE = "2026-08-24 00:00"

# ---- Ereignisse (automatisch erkannt, Skript 11) + Notizen
NOTIZEN = {
    "2026-03-28 02": "Anfang der Messung: Problem wurde entdeckt, dann etwas dagegen unternommen",
    "2026-03-30 15": "kurz nach Sensorstart Küche-Sockel (13:50), Einlaufphase",
    "2026-07-11 23": "kurze Spitze; laut Hr. Grimmer vielleicht Messungenauigkeit. Davor Schlafzimmer-CO₂ 1767 ppm",
    "2026-07-16 12": "nur im Keller, Keller laut Hr. Grimmer weniger wichtig",
    "2026-07-20 11": "tagsüber alle Wohnräume hoch; laut Hr. Grimmer wahrscheinlich Fenster zu",
    "2026-08-11 20": "kurze Spitze; laut Hr. Grimmer vielleicht Messungenauigkeit. Schlafzimmer-CO₂ ~1050",
    "2026-08-23 01": "nachts, einen Tag vor dem Einbau der Anlage, Ursache unbekannt",
    "2026-10-11 01": "Küche-CO₂ erreicht am selben Tag den Höchstwert (1778 ppm)",
}
ev = pd.read_csv("analyse/ereignisse_radon.csv", parse_dates=["von", "bis"])
ereignisse = []
for r in ev.itertuples():
    key = r.von.strftime("%Y-%m-%d %H")
    ereignisse.append(dict(art="Radon-Ereignis", von=r.von.strftime("%Y-%m-%d %H:%M"), bis=r.bis.strftime("%Y-%m-%d %H:%M"),
                           raeume=r.Raeume.replace(",", ", ").replace("KuecheSockel", "Küche Sockel").replace("Kueche", "Küche")
                                          .replace("Buero", "Büro").replace("Schlaf", "Schlafzimmer"),
                           peak=int(r.Peak), notiz=NOTIZEN.get(key, "")))
# ---- gleichzeitige Resets aller Sensoren (Skript 06)
RESETS = ["2026-04-16 07:00", "2026-04-30 16:00", "2026-07-06 06:00", "2026-08-30 11:00", "2026-09-10 14:00", "2026-09-16 15:00"]
for t in RESETS:
    ereignisse.append(dict(art="Sensor-Reset", von=t, bis=t, raeume="alle Sensoren", peak=None,
                           notiz="Betriebszeit aller Sensoren springt auf 0; Ursache laut Hr. Grimmer unbekannt"))
ereignisse.sort(key=lambda e: e["von"])

# ---- Kennzahlen je Periode (Median der Stundenwerte)
PER = [("überwiegend gelüftet", "01.04.–17.06.", "2026-04-01", "2026-06-17"), ("weniger gelüftet", "22.06.–30.07.", "2026-06-22", "2026-07-30"),
       ("Urlaub (Haus zu)", "01.08.–06.08.", "2026-08-01", "2026-08-06"), ("nach Urlaub, vor Anlage", "07.08.–23.08.", "2026-08-07", "2026-08-23"),
       ("nach Einbau der Anlage", "25.08.–22.09.", "2026-08-25", "2026-09-22"), ("Herbst (im Messfehler ±30)", "23.09.–13.10.", "2026-09-23", "2026-10-13")]
tab = []
for nm, lab, a, b in PER:
    seg = h.loc[a:b + " 23:59"] if False else h.loc[a:b]
    tab.append(dict(name=nm, zeitraum=lab, **{k: (None if pd.isna(seg[k].median()) else int(round(seg[k].median()))) for k, *_ in RAEUME}))

def med(k, a, b):
    return int(round(h.loc[a:b][k].median()))

wohn = ["wohn", "kueche", "buero", "schlaf"]
mx = h[[r[0] for r in RAEUME]].stack().idxmax()
kpi = dict(
    zeilen=int(len(df)), tage=int((h.index[-1] - h.index[0]).days),
    n_ereignisse=int((ev.shape[0])), n_resets=len(RESETS),
    max_wert=int(round(h.loc[mx[0], mx[1]])), max_raum=[r[1] for r in RAEUME if r[0] == mx[1]][0], max_zeit=mx[0].strftime("%d.%m.%Y %H:%M"),
    urlaub_wohn=int(round(h.loc["2026-08-02":"2026-08-06", wohn].stack().median())),
    normal_wohn=int(round(h.loc["2026-08-25":"2026-09-22", wohn].stack().median())),
    keller_a=med("technik", "2026-04-01", "2026-06-17"), keller_b=med("technik", "2026-06-22", "2026-07-30"),
    keller_d=med("technik", "2026-08-25", "2026-09-22"),
)
OGc = ["buero", "kueche", "wohn", "schlaf"]
OG = h[OGc].mean(axis=1); OGmax = h[OGc].max(axis=1)
U0, U1, INST = pd.Timestamp("2026-07-31 18:00"), pd.Timestamp("2026-08-06 19:30"), pd.Timestamp(WENDE)
okm = (h.index >= "2026-04-01") & ~((h.index >= U0) & (h.index < U1))
vor, nach = okm & (h.index < INST), h.index >= INST
kpi.update(og_pre=int(round(OG[vor].mean())), og_post=int(round(OG[nach].mean())),
           p100_pre=round(100 * (OGmax[vor] > 100).sum() / OGmax[vor].count(), 1), p100_post=round(100 * (OGmax[nach] > 100).sum() / OGmax[nach].count(), 1))
print(json.dumps(kpi, ensure_ascii=False, indent=1))

def prof(s):
    g = s.groupby(s.index.hour)
    return {"med": g.median().round(1).tolist(), "q1": g.quantile(.25).round(1).tolist(), "q3": g.quantile(.75).round(1).tolist()}
tag = {}
for k, ser in [("og", OG)] + [(r[0], h[r[0]]) for r in RAEUME]:
    a, b = prof(ser[vor].dropna()), prof(ser[nach].dropna())
    tag[k] = dict(pre=a["med"], pre25=a["q1"], pre75=a["q3"], post=b["med"], post25=b["q1"], post75=b["q3"])
wk = pd.read_csv("analyse/wirkung_woche.csv", parse_dates=["t"])
woche = [dict(t=r.t.strftime("%Y-%m-%d"), p100=None if pd.isna(r.p100) else round(float(r.p100), 1), exc=None if pd.isna(r.exc) else round(float(r.exc), 1)) for r in wk.itertuples()]
print(pd.DataFrame(tab).to_string())

daten = dict(start="2026-03-24 00:00", serien=serien, raeume=[dict(k=a, name=b, slot=d) for a, b, c, d in RAEUME],
             phasen=PHASEN, wende=WENDE, ereignisse=ereignisse, perioden=tab, kpi=kpi, tag=tag, woche=woche)
tpl = open("dashboard/template.html", encoding="utf-8").read()
out = tpl.replace("/*__DATEN__*/null", json.dumps(daten, ensure_ascii=False, separators=(",", ":")))
open("dashboard.html", "w", encoding="utf-8").write(out)
print("dashboard.html:", round(len(out) / 1024), "KB")
