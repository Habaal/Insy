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
    dict(id="fenster", name="Keller-Fenster offen (Hypothese)", von="2026-04-01 00:00", bis="2026-06-17 23:59",
         frage="Frage 2: Welche zwei Fenster, von wann bis wann?"),
    dict(id="urlaub", name="Urlaub", von="2026-07-31 18:00", bis="2026-08-06 19:30",
         frage="Frage 1: Stimmt der Zeitraum? Gab es weitere Abwesenheiten?"),
]
WENDE = "2026-08-24 00:00"

# ---- Ereignisse (automatisch erkannt, Skript 11) + Notizen
NOTIZEN = {
    "2026-03-28 02": "Anlaufphase der Messung",
    "2026-03-30 15": "kurz nach Sensorstart Küche-Sockel (13:50)",
    "2026-07-11 23": "kurze Spitze; davor Schlafzimmer-CO₂ 1767 ppm (Frage 7)",
    "2026-07-16 12": "nur Keller, Sägezahn-Vorstufe (Frage 5)",
    "2026-07-20 11": "tagsüber alle Wohnräume hoch, CO₂ normal (Frage 6)",
    "2026-08-11 20": "kurze Spitze; Schlafzimmer-CO₂ ~1050 (Frage 7)",
    "2026-08-23 01": "nachts, Büro nicht betroffen (Frage 7)",
    "2026-10-11 01": "Küche-CO₂-Rekord 1778 ppm am selben Tag",
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
                           notiz="Betriebszeit aller Sensoren springt auf 0 (Frage 10)"))
ereignisse.sort(key=lambda e: e["von"])

# ---- Kennzahlen je Periode (Median der Stundenwerte)
PER = [("A", "01.04.–17.06.", "2026-04-01", "2026-06-17"), ("B", "22.06.–30.07.", "2026-06-22", "2026-07-30"),
       ("Urlaub", "01.08.–06.08.", "2026-08-01", "2026-08-06"), ("C", "07.08.–23.08.", "2026-08-07", "2026-08-23"),
       ("D", "25.08.–22.09.", "2026-08-25", "2026-09-22"), ("E", "23.09.–13.10.", "2026-09-23", "2026-10-13")]
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
print(json.dumps(kpi, ensure_ascii=False, indent=1))
print(pd.DataFrame(tab).to_string())

daten = dict(start="2026-03-24 00:00", serien=serien, raeume=[dict(k=a, name=b, slot=d) for a, b, c, d in RAEUME],
             phasen=PHASEN, wende=WENDE, ereignisse=ereignisse, perioden=tab, kpi=kpi)
tpl = open("dashboard/template.html", encoding="utf-8").read()
out = tpl.replace("/*__DATEN__*/null", json.dumps(daten, ensure_ascii=False, separators=(",", ":")))
open("dashboard.html", "w", encoding="utf-8").write(out)
print("dashboard.html:", round(len(out) / 1024), "KB")
