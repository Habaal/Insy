import pandas as pd, numpy as np
pd.set_option("display.width",250); pd.set_option("display.max_columns",60); pd.set_option("display.max_rows",400)
RAUM=["Buero","Kueche","Kueche - Sockel","Schlafzimmer","Technikraum","Werkstatt","Wohnzimmer"]
def laden():
    df=pd.read_csv("data/radon_sample_data.csv")
    df["t"]=pd.to_datetime(df["Zeit (Europe/Vienna)"])
    df=df.drop(columns=["Zeit (UTC)","Zeit (Europe/Vienna)"]).set_index("t")
    return df
def kurz(c):
    return (c.replace("Kueche (Luft) – ","KuecheL_").replace("Schlafzimmer – ","Schlaf_").replace(" – Radon (Bq/m³)","_Rn")
            .replace(" – Betriebszeit (min)","_BZ").replace("Kueche - Sockel","KuecheSockel").replace("Wetter – ","W_")
            .replace(" – ","_").replace(" ","_"))
