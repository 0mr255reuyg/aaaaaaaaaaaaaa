"""
BIST Swing Trade Tarayıcı - v2
Sağlam, hafif, takılmayan versiyon.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# BIST HİSSE LİSTESİ (~220 hisse, .IS uzantılı)
# ─────────────────────────────────────────────────────────────────────────────
TICKERS = [
    "THYAO.IS","EREGL.IS","GARAN.IS","AKBNK.IS","YKBNK.IS","ISCTR.IS","KCHOL.IS",
    "SASA.IS","BIMAS.IS","FROTO.IS","TUPRS.IS","ASELS.IS","TOASO.IS","PGSUS.IS",
    "HALKB.IS","VAKBN.IS","TKFEN.IS","ENKAI.IS","KOZAL.IS","KRDMD.IS","PETKM.IS",
    "TTKOM.IS","TAVHL.IS","OTKAR.IS","SAHOL.IS","ARCLK.IS","VESTL.IS","MGROS.IS",
    "EKGYO.IS","ULKER.IS","TCELL.IS","SISE.IS","DOHOL.IS","AEFES.IS","LOGO.IS",
    "MAVI.IS","BRISA.IS","CCOLA.IS","ALARK.IS","AKSEN.IS","AYGAZ.IS","TSKB.IS",
    "SODA.IS","CIMSA.IS","OYAKC.IS","HEKTS.IS","DOAS.IS","TTRAK.IS","KARSN.IS",
    "ADEL.IS","NUHCM.IS","GUBRF.IS","LINK.IS","TRKCM.IS","AKGRT.IS","ANSGR.IS",
    "AGESA.IS","ALKIM.IS","SARKY.IS","KUTPO.IS","ERBOS.IS","DMSAS.IS","KAPLM.IS",
    "CLEBI.IS","YATAS.IS","MPARK.IS","ODAS.IS","BERA.IS","INDES.IS","OBASE.IS",
    "SKBNK.IS","KLNMA.IS","ISGYO.IS","RYGYO.IS","DZGYO.IS","TRGYO.IS","VKGYO.IS",
    "KOZAA.IS","KRDMA.IS","KRDMB.IS","GEREL.IS","SODSN.IS","BANVT.IS","AVOD.IS",
    "PKART.IS","SANEL.IS","KATMR.IS","FONET.IS","KAREL.IS","SOKM.IS","TBORG.IS",
    "GWIND.IS","ENERY.IS","EUPWR.IS","BOSSA.IS","CELHA.IS","EGEEN.IS","GOODY.IS",
    "HATEK.IS","IHLAS.IS","JANTS.IS","KORDS.IS","KRSAN.IS","PETUN.IS","PINSU.IS",
    "SANFM.IS","SEKUR.IS","TATGD.IS","TMSN.IS","TUKAS.IS","ULUUN.IS","UNLU.IS",
    "YAPRK.IS","YUNSA.IS","AAIGM.IS","ACSEL.IS","AKBLK.IS","ALFAS.IS","ALVES.IS",
    "ANELE.IS","ARDYZ.IS","ARENA.IS","ARSAN.IS","AVGYO.IS","AZTEK.IS","BAKAB.IS",
    "BALAT.IS","BARMA.IS","BEGYO.IS","BFREN.IS","BIGCH.IS","BLCYT.IS","BMSTL.IS",
    "BRKSN.IS","BRSAN.IS","BURCE.IS","BURVA.IS","CEMAS.IS","CEOEM.IS","COMDO.IS",
    "COSMO.IS","CUSAN.IS","CWENE.IS","DATA.IS","DERHL.IS","DESA.IS","DESPC.IS",
    "DEVA.IS","DITAS.IS","DNISI.IS","DOBUR.IS","DURDO.IS","DYOBY.IS","ECILC.IS",
    "ECZYT.IS","EDIP.IS","EGEPO.IS","EGSER.IS","EMKEL.IS","EMNIS.IS","ENPLA.IS",
    "EPLAS.IS","ERSU.IS","ESCOM.IS","ETILR.IS","EUHOL.IS","EURO.IS","EUROB.IS",
    "FBASE.IS","FENER.IS","FORMT.IS","FORTE.IS","FRIGO.IS","GEDIK.IS","GESAN.IS",
    "GLBMD.IS","GOLDS.IS","GRNYO.IS","GRSEL.IS","GSDDE.IS","GSDHO.IS","GSRAY.IS",
    "GULFA.IS","GVENS.IS","HTTBT.IS","HUNER.IS","HURGZ.IS","ICBCT.IS","IHLGM.IS",
    "IHEVA.IS","ISATR.IS","ISKPL.IS","ISKUR.IS","ISYAT.IS","ITTFH.IS","IZTAR.IS",
    "KFEIN.IS","KONTR.IS","KONYA.IS","KRPLA.IS","KRVGD.IS","KSTUR.IS","KTLEV.IS",
    "KTSKR.IS","KWPWR.IS","LIDER.IS","LKMNH.IS","MEMSA.IS","MEGES.IS","MOBTL.IS",
    "MRSHL.IS","NTGAZ.IS","NUGYO.IS","OSMEN.IS","OZBAL.IS","PENGD.IS","PKENT.IS",
    "PRZMA.IS","QNBFB.IS","QNBFL.IS","RUBNS.IS","SAMAT.IS","SANKO.IS","SEGYO.IS",
    "SEKFK.IS","SELGD.IS","SEZGI.IS","SILVR.IS","SKYLP.IS","TEBNK.IS","TMPOL.IS",
    "TREYD.IS","TUCLK.IS","TUMTK.IS","UZERB.IS","VERUS.IS","VKING.IS","YESIL.IS",
    "YGGYO.IS","YKSGR.IS","ZEDUR.IS","BJKAS.IS","EKIZ.IS","IHGZT.IS","FENER.IS",
    "GSRAY.IS","BJKAS.IS","TSPOR.IS","DEVA.IS","SELEC.IS","GOLTS.IS","ISGSY.IS",
    "ISDMR.IS","KOZA1.IS","ALTNY.IS","DMRGD.IS","PRKME.IS","FADE.IS","ARAT.IS",
]
TICKERS = list(dict.fromkeys(TICKERS))  # tekrarlari kaldir

# ─────────────────────────────────────────────────────────────────────────────
# TEKNİK GÖSTERGE FONKSİYONLARI
# ─────────────────────────────────────────────────────────────────────────────

def calc_rsi(close: pd.Series, period=14) -> float:
    delta = close.diff()
    gain  = delta.clip(lower=0).ewm(alpha=1/period, min_periods=period).mean()
    loss  = (-delta.clip(upper=0)).ewm(alpha=1/period, min_periods=period).mean()
    rs    = gain / loss.replace(0, np.nan)
    val   = 100 - 100 / (1 + rs)
    return float(val.iloc[-1]) if not val.empty else 50.0


def calc_macd(close: pd.Series):
    ema12  = close.ewm(span=12, adjust=False).mean()
    ema26  = close.ewm(span=26, adjust=False).mean()
    line   = ema12 - ema26
    sig    = line.ewm(span=9, adjust=False).mean()
    hist   = line - sig
    h_now  = float(hist.iloc[-1])
    h_prev = float(hist.iloc[-2]) if len(hist) > 1 else 0.0
    return float(line.iloc[-1]), float(sig.iloc[-1]), h_now, h_prev


def calc_atr(high, low, close, period=14) -> float:
    prev = close.shift(1)
    tr   = pd.concat([high - low,
                      (high - prev).abs(),
                      (low  - prev).abs()], axis=1).max(axis=1)
    return float(tr.ewm(span=period, adjust=False).mean().iloc[-1])


# ─────────────────────────────────────────────────────────────────────────────
# TEK HİSSE PUANLAMA
# ─────────────────────────────────────────────────────────────────────────────

def score_ticker(ticker: str) -> dict | None:
    """
    Bir hisse için teknik analiz tabanlı puan hesapla.
    Döndürülen dict içinde 'elendi' alanı dolu ise hisse filtreyi geçemedi.
    """
    try:
        raw = yf.download(ticker, period="1y", interval="1d",
                          auto_adjust=True, progress=False, timeout=10)

        # MultiIndex sütunları düzleştir (yfinance 0.2.x davranışı)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        df = raw[["Close", "High", "Low", "Volume"]].dropna()
        if len(df) < 60:
            return None

        close = df["Close"].squeeze()
        high  = df["High"].squeeze()
        low   = df["Low"].squeeze()
        vol   = df["Volume"].squeeze()

        price = float(close.iloc[-1])

        # ── Hareketli Ortalamalar ────────────────────────────────────────
        ma50       = float(close.rolling(50).mean().iloc[-1])
        ma200_s    = close.rolling(200).mean()
        ma200      = float(ma200_s.iloc[-1]) if not np.isnan(ma200_s.iloc[-1]) else None

        above_ma50  = price > ma50
        above_ma200 = (ma200 is None) or (price > ma200)

        # ZORUNLU TREND FİLTRESİ
        if not (above_ma50 and above_ma200):
            return {
                "ticker": ticker, "skor": 0,
                "elendi": "MA50/MA200 Altı"
            }

        # ── Teknik Göstergeler ────────────────────────────────────────────
        rsi_val             = calc_rsi(close)
        m_line, m_sig, m_h, m_hp = calc_macd(close)
        atr_val             = calc_atr(high, low, close)
        atr_pct             = (atr_val / price) * 100

        vol5       = float(vol.iloc[-5:].mean())
        vol20      = float(vol.iloc[-20:].mean())
        vol_ratio  = vol5 / vol20 if vol20 > 0 else 1.0

        # ── PUANLAMA (Toplam maks 90) ─────────────────────────────────────

        # RSI  (0-25)
        if   rsi_val < 30:         rsi_p = 3
        elif rsi_val < 40:         rsi_p = 10
        elif rsi_val < 50:         rsi_p = 16
        elif rsi_val <= 62:        rsi_p = 25   # ideal swing bölgesi
        elif rsi_val <= 70:        rsi_p = 18
        elif rsi_val <= 80:        rsi_p = 8
        else:                      rsi_p = 2

        # MACD (0-25)
        macd_guclu  = m_h > 0 and m_h > m_hp and m_line > m_sig
        hist_buyuyor= m_h > 0 and m_h > m_hp
        if   macd_guclu:           macd_p = 25
        elif hist_buyuyor:         macd_p = 18
        elif m_h > 0:              macd_p = 12
        elif m_line > m_sig:       macd_p = 8
        else:                      macd_p = 0

        # Hacim (0-15)
        if   vol_ratio > 2.0:      vol_p = 15
        elif vol_ratio > 1.5:      vol_p = 12
        elif vol_ratio > 1.2:      vol_p = 8
        elif vol_ratio >= 1.0:     vol_p = 5
        else:                      vol_p = 0

        # ATR Volatilite (0-15) — swing için %1.5-3 ideal
        if   atr_pct < 0.8:        atr_p = 1
        elif atr_pct < 1.5:        atr_p = 6
        elif atr_pct <= 3.0:       atr_p = 15
        elif atr_pct <= 5.0:       atr_p = 9
        elif atr_pct <= 7.0:       atr_p = 4
        else:                      atr_p = 1

        # Bonus (0-10)
        bonus = 0
        if ma200 and ma50 > ma200:                  bonus += 5   # golden cross yapısı
        ma50_dist = ((price - ma50) / ma50) * 100
        if 1 <= ma50_dist <= 10:                    bonus += 5
        elif 0 < ma50_dist < 1:                     bonus += 2

        toplam = min(rsi_p + macd_p + vol_p + atr_p + bonus, 90)

        # MACD etiketi
        if   macd_guclu:    macd_lbl = "🔥 Güçlü"
        elif hist_buyuyor:  macd_lbl = "📈 Büyüyor"
        elif m_h > 0:       macd_lbl = "✅ Pozitif"
        else:               macd_lbl = "❌ Negatif"

        return {
            "ticker":    ticker,
            "fiyat":     round(price, 2),
            "skor":      round(toplam, 1),
            "rsi":       round(rsi_val, 1),
            "macd_lbl":  macd_lbl,
            "atr_pct":   round(atr_pct, 2),
            "vol_ratio": round(vol_ratio, 2),
            "rsi_p":     rsi_p,
            "macd_p":    macd_p,
            "vol_p":     vol_p,
            "atr_p":     atr_p,
            "bonus":     bonus,
            "ma50":      round(ma50, 2),
            "ma200":     round(ma200, 2) if ma200 else "N/A",
            "elendi":    None,
        }

    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# STREAMLIT ARAYÜZ
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="BIST Swing Tarayıcı",
    page_icon="📈",
    layout="wide"
)

st.title("📈 BIST Swing Trade Tarayıcı")
st.caption("1 aylık swing trade için teknik analiz tabanlı puanlama • Max 90 puan")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Tarama Ayarları")

    min_skor  = st.slider("Minimum AL Skoru", 40, 85, 60, 5)
    n_hisse   = st.slider("Taranacak Hisse Sayısı", 30, len(TICKERS), 200, 10)
    gecikme   = st.slider("İstek Gecikmesi (sn)", 0.1, 1.0, 0.25, 0.05,
                          help="yfinance rate-limit koruması")

    st.divider()
    st.markdown("**Sonuç Filtreleri**")
    min_rsi   = st.slider("Min RSI",      0, 50,  35)
    max_rsi   = st.slider("Max RSI",     50, 100, 78)
    min_vol   = st.slider("Min Hacim Oranı (5g/20g)", 0.5, 3.0, 1.0, 0.1)

    st.divider()
    basla = st.button("🚀 Taramayı Başlat", type="primary", use_container_width=True)

# ── Tarama ───────────────────────────────────────────────────────────────────
if basla:
    taranacak = TICKERS[:n_hisse]
    sonuclar  = []
    elenenler = []
    hatalar   = 0

    prog  = st.progress(0, text="Başlatılıyor...")
    durum = st.empty()

    for i, tkr in enumerate(taranacak):
        durum.markdown(f"⏳ Taranan: **{tkr}**  ({i+1}/{len(taranacak)})")
        r = score_ticker(tkr)

        if r is None:
            hatalar += 1
        elif r.get("elendi"):
            elenenler.append(r)
        else:
            sonuclar.append(r)

        prog.progress((i + 1) / len(taranacak))
        time.sleep(gecikme)

    prog.empty()
    durum.empty()

    # ── DataFrame oluştur ve filtrele ────────────────────────────────────────
    if sonuclar:
        df = (pd.DataFrame(sonuclar)
                .sort_values("skor", ascending=False)
                .reset_index(drop=True))
        df_f  = df[(df["rsi"] >= min_rsi) & (df["rsi"] <= max_rsi) & (df["vol_ratio"] >= min_vol)]
        df_al = df_f[df_f["skor"] >= min_skor]
    else:
        df = df_f = df_al = pd.DataFrame()

    # ── Özet Metrikler ───────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔍 Taranan",        n_hisse)
    c2.metric("✅ Trend Üstü",     len(sonuclar))
    c3.metric("🚀 AL Listesi",     len(df_al))
    c4.metric("⚠️ Elenen/Hata",   f"{len(elenenler)}/{hatalar}")

    st.divider()

    # ── AL LİSTESİ TABLOSU ───────────────────────────────────────────────────
    st.subheader(f"🚀 AL Listesi — {len(df_al)} hisse  (≥{min_skor} puan)")

    if df_al.empty:
        st.warning("Filtreyi karşılayan hisse bulunamadı. Skoru veya filtreleri gevşetin.")
    else:
        kolon_map = {
            "ticker":    "Hisse",
            "fiyat":     "Fiyat ₺",
            "skor":      "Skor /90",
            "rsi":       "RSI",
            "macd_lbl":  "MACD",
            "atr_pct":   "ATR %",
            "vol_ratio": "Hacim Ort.",
            "rsi_p":     "RSI Puan",
            "macd_p":    "MACD Puan",
            "vol_p":     "Hacim Puan",
            "atr_p":     "ATR Puan",
            "bonus":     "Bonus",
            "ma50":      "MA50",
            "ma200":     "MA200",
        }
        df_goster = df_al.rename(columns=kolon_map)[list(kolon_map.values())]

        def renk_skor(val):
            if isinstance(val, (int, float)):
                if val >= 72: return "background-color:#1a6b3c;color:white"
                if val >= 58: return "background-color:#2d9e5f;color:white"
                if val >= 45: return "background-color:#c8860a"
            return ""

        styled = (df_goster.style
                  .applymap(renk_skor, subset=["Skor /90"])
                  .format({"Fiyat ₺": "{:.2f}", "Skor /90": "{:.1f}",
                           "RSI": "{:.1f}", "ATR %": "{:.2f}",
                           "Hacim Ort.": "{:.2f}"}))

        st.dataframe(styled, use_container_width=True, height=480)

        csv = df_al.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "📥 AL Listesini CSV İndir", csv,
            f"bist_al_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )

    # ── SKOR GRAFİĞİ ─────────────────────────────────────────────────────────
    if not df.empty:
        st.divider()
        st.subheader("📊 Skor Dağılımı — İlk 35 Hisse")
        top = df.head(35)

        fig = go.Figure()
        for kolon, renk, isim in [
            ("rsi_p",  "#4A90D9", "RSI"),
            ("macd_p", "#F4A83A", "MACD"),
            ("vol_p",  "#50C878", "Hacim"),
            ("atr_p",  "#E74C3C", "ATR"),
            ("bonus",  "#9B59B6", "Bonus"),
        ]:
            fig.add_trace(go.Bar(
                x=top["ticker"], y=top[kolon],
                name=isim, marker_color=renk
            ))

        fig.add_hline(y=min_skor, line_dash="dash", line_color="white",
                      annotation_text=f"AL Eşiği ({min_skor})")
        fig.update_layout(
            barmode="stack", height=420,
            xaxis_tickangle=-50,
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117", font_color="white",
            legend=dict(orientation="h", y=1.1),
            margin=dict(l=10, r=10, t=30, b=90),
            title="Her renk bir kriter — istif yüksekliği = toplam skor"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── TOP 5 KART ───────────────────────────────────────────────────────────
    if not df_al.empty:
        st.divider()
        st.subheader("🏆 En İyi 5 Hisse")
        top5 = df_al.head(5)
        cols = st.columns(len(top5))
        emojiler = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

        for idx, (_, row) in enumerate(top5.iterrows()):
            if row["skor"] >= 72:   brd = "#1a6b3c"
            elif row["skor"] >= 58: brd = "#2d9e5f"
            else:                   brd = "#c8860a"

            cols[idx].markdown(f"""
<div style="background:#1e2d3d;padding:14px;border-radius:10px;
            border-left:4px solid {brd};font-size:13px;line-height:1.8;">
<b>{emojiler[idx]} {row['ticker']}</b><br>
💰 <b>{row['fiyat']} ₺</b><br>
⭐ Skor: <b>{row['skor']}/90</b><br>
📊 RSI: {row['rsi']}<br>
📉 MACD: {row['macd_lbl']}<br>
📦 Hacim: ×{row['vol_ratio']}<br>
🎯 ATR: %{row['atr_pct']}<br>
〰 MA50: {row['ma50']}
</div>""", unsafe_allow_html=True)

    # ── ELENENLERİ GÖSTER ────────────────────────────────────────────────────
    if elenenler:
        with st.expander(f"⛔ Trend Altındaki Hisseler ({len(elenenler)} adet) — görmek için tıkla"):
            df_el = pd.DataFrame(elenenler)[["ticker", "elendi"]]
            df_el.columns = ["Hisse", "Eleme Sebebi"]
            st.dataframe(df_el, use_container_width=True)

    st.success(f"✅ Tarama tamamlandı — {datetime.now().strftime('%d.%m.%Y %H:%M')}")

# ── Başlangıç Ekranı ─────────────────────────────────────────────────────────
else:
    st.info("⬅️ Sol panelden ayarları yapıp **Taramayı Başlat** butonuna tıklayın.")

    st.markdown("""
### Puanlama Sistemi (Toplam 90 Puan)

| Kriter | Max Puan | İdeal Aralık |
|--------|----------|-------------|
| **RSI** | 25 | 40–62 arası |
| **MACD** | 25 | Histogram büyüyor + pozitif |
| **Hacim** | 15 | 5g/20g > 1.2× |
| **ATR Volatilite** | 15 | Fiyatın %1.5–3'ü |
| **Bonus** | 10 | MA Golden Cross + MA50 mesafesi |

> **Trend Filtresi zorunlu:** Fiyat MA50 veya MA200 altındaysa hisse otomatik elenir.

**🟢 70+ → Güçlü AL &nbsp;&nbsp;&nbsp; 🟡 55–69 → Orta &nbsp;&nbsp;&nbsp; ⚪ <55 → Zayıf**
    """)
