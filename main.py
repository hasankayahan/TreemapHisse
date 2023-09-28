import pandas as pd
import requests
from plotly import offline
import plotly.express as px
import lxml  # lxml kütüphanesini içe aktarın

url = "https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx#page-1"

# Tablo 1
tablo = pd.read_html(requests.get(url).text, flavor="lxml")[2]
sektör = pd.DataFrame({
    "Hisse": tablo["Kod"],
    "Sektör": tablo["Sektör"],
    "Piyasa Değeri (mn $)": tablo["Piyasa Değeri (mn $)"].str.replace(',', '.').str.replace('.', '', 1).astype(float)
})

# Tablo 2
tablo2 = pd.read_html(requests.get(url).text, flavor="lxml")[7]
tablo2["Günlük Getiri (%)"] = tablo2["Günlük Getiri (%)"].replace('-', '0').str.replace(',', '.').astype(float) / 100
getiri = pd.DataFrame({
    "Hisse": tablo2["Kod"],
    "Getiri (%)": tablo2["Günlük Getiri (%)"]
})

# Verileri Birleştir
df = pd.merge(sektör, getiri, on="Hisse")

# Renkler
renk_aralık = [-10, -5, -0.01, 0, 0.01, 5, 10]
df["Renk"] = pd.cut(df["Getiri (%)"], bins=renk_aralık, labels=["red", "indianred", "lightpink", "lightgreen", "lime", "green"])

# Plotly Grafiği
fig = px.treemap(df, path=[px.Constant("Borsa İstanbul"), "Sektör", "Hisse"],
                 values="Piyasa Değeri (mn $)", color="Renk",
                 custom_data=["Getiri (%)", "Sektör"],
                 color_discrete_map={"(?)": "#262931", "red": "red",
                                     "indianred": "indianred", "lightpink": "lightpink",
                                     'lightgreen': 'lightgreen', 'lime': 'lime', 'green': 'green'})

fig.update_traces(
    hovertemplate="<br>".join([
        "Hisse: %{label}",
        "Piyasa Değeri (mn $): %{value}",
        "Getiri: %{customdata[0]}",
        "Sektör: %{customdata[1]}"
    ])
)

fig.data[0].texttemplate = "<b>%{label}</b><br>%{customdata[0]} %"

# Grafiği Kaydet
offline.plot(fig, filename="grafikler/grafik.html")
