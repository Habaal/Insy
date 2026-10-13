import pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_columns",50); pd.set_option("display.max_rows",100)
df=pd.read_csv("data/radon_sample_data.csv")
df["t"]=pd.to_datetime(df["Zeit (Europe/Vienna)"])
df=df.drop(columns=["Zeit (UTC)","Zeit (Europe/Vienna)"]).set_index("t")
print(df.shape, df.index.min(), df.index.max())
d=df.describe().T[["count","min","mean","max"]]
d["first"]=[df[c].first_valid_index() for c in df.columns]
d["last"]=[df[c].last_valid_index() for c in df.columns]
print(d)
