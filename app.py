import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import time

# -----------------------------------------------------------------------------
# 1. AYARLAR & TASARIM (ANİMASYONLU)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="BIST PRO v4", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp { 
        background: linear-gradient(135deg, #0e1117 0%, #1a1d24 100%); 
        color: #ffffff; 
    }
    
    /* Butonlar */
    .stButton>button {
        background: linear-gradient(135deg, #00ff41 0%, #00cc33 100%); 
        color: #000000; 
        font-weight: bold;
        border: none;
        padding: 15px 30px; 
        border-radius: 10px; 
        width: 100%;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 255, 65, 0.3);
    }
    .stButton>button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 255, 65, 0.5);
    }
    
    /* Metrik Kartları */
    .stMetric { 
        background: linear-gradient(135deg, #1f2937 0%, #2d3748 100%); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #00ff41; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetricValue"] { color: #00ff41; font-size: 24px; }
    div[data-testid="stMetricLabel"] { color: #aaaaaa; }
    
    /* Hisse Kartları (Animasyonlu) */
    .stock-card {
        background: linear-gradient(135deg, #1f2937 0%, #2d3748 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #374151;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        animation: slideIn 0.5s ease-out;
    }
    .stock-card:hover {
        transform: translateY(-5px);
        border-color: #00ff41;
        box-shadow: 0 8px 25px rgba(0, 255, 65, 0.2);
    }
    
    /* Stop-Loss & TP Kutuları */
    .sl-box { 
        background: rgba(255, 68, 68, 0.1); 
        border-left: 4px solid #ff4444; 
        padding: 10px; 
        margin: 10px 0; 
        border-radius: 8px;
    }
    .tp-box { 
        background: rgba(0, 255, 65, 0.1); 
        border-left: 4px solid #00ff41; 
        padding: 10px; 
        margin: 10px 0; 
        border-radius: 8px;
    }
    .ai-box { 
        background: rgba(0, 204, 255, 0.1); 
        border-left: 4px solid #00ccff; 
        padding: 15px; 
        margin: 10px 0; 
        border-radius: 8px;
        font-style: italic;
    }
    
    /* Animasyonlar */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 255, 65, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(0, 255, 65, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 255, 65, 0); }
    }
    .loading {
        animation: pulse 2s infinite;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. VERİ FONKSİYONLARI (DÜZELTİLMİŞ)
# -----------------------------------------------------------------------------

def get_bist100_tickers():
    return [
        "THYAO.IS", "ASELS.IS", "GARAN.IS", "AKBNK.IS", "EREGL.IS", "TUPRS.IS", 
        "SASA.IS", "KCHOL.IS", "SAHOL.IS", "BIMAS.IS", "MGROS.IS", "FROTO.IS", 
        "TOASO.IS", "TCELL.IS", "TTKOM.IS", "HEKTS.IS", "ALARK.IS", "DOHOL.IS",
        "ISCTR.IS", "YKBNK.IS", "HALKB.IS", "VAKBN.IS", "KOZAL.IS", "GLYHO.IS",
        "ENKAI.IS", "AKSA.IS", "PETKM.IS", "TTRAK.IS", "MAVI.IS", "AEFES.IS",
        "SOKM.IS", "CCOLA.IS", "ANSGR.IS", "PGSUS.IS", "ULKER.IS", "KORDS.IS",
        "TAVHL.IS", "OYAKC.IS", "ISGYO.IS", "AKFGY.IS", "EKGYO.IS", "VESBE.IS",
        "BRISA.IS", "FLO.IS", "DEVA.IS", "CELHA.IS", "MONTI.IS", "SMART.IS",
        "GUBRF.IS", "POLHO.IS", "CIMSA.IS", "NUHOL.IS", "BOLUC.IS", "KARTN.IS",
        "TRKCM.IS", "SELEC.IS", "LOGO.IS", "YATAS.IS", "USAK.IS", "DENGE.IS",
        "FORMT.IS", "ALTNY.IS", "KFEIN.IS", "BIZIM.IS", "CATAS.IS", "CRDFA.IS",
        "DAGI.IS", "DERIM.IS", "DESA.IS", "DMSAS.IS", "DOAS.IS", "ECILC.IS",
        "EDATA.IS", "EGEEN.IS", "EMKEL.IS", "ERBOS.IS", "ERSU.IS", "ETLER.IS",
        "FENER.IS", "FINBN.IS", "FKORE.IS", "GOODY.IS", "GRHOL.IS", "GSYO.IS",
        "HATEK.IS", "HUBVC.IS", "ICBCT.IS", "IHLAS.IS", "IHLGM.IS", "INDES.IS",
        "ISDMR.IS", "ISKUR.IS", "IZMDC.IS", "KARSN.IS", "KAYSE.IS", "KLBRN.IS",
        "KONTR.IS", "KUTPO.IS", "LKNDY.IS", "MAVI.IS", "MEBRS.IS", "MENSA.IS"
    ]

def fetch_single_data(ticker):
    """Tek hisse verisi çeker (Daha güvenilir)"""
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df.empty or len(df) < 60:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if 'Close' not in df.columns:
            return None
        return df
    except:
        return None

def calculate_indicators(df):
    """Teknik indikatörleri hesapla"""
    close = df['Close'].values
    high = df['High'].values
    low = df['Low'].values
    
    # RSI (14)
    delta = np.diff(close)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = np.mean(gain[:14]) if len(gain) >= 14 else 0
    avg_loss = np.mean(loss[:14]) if len(loss) >= 14 else 1
    rsi = 50
    for i in range(14, len(close)):
        avg_gain = (avg_gain * 13 + gain[i]) / 14
        avg_loss = (avg_loss * 13 + loss[i]) / 14
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = pd.Series(close).ewm(span=12, adjust=False).mean()
    exp2 = pd.Series(close).ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    
    # ATR
    tr = high - low
    atr = np.mean(tr[-14:]) if len(tr) >= 14 else close[-1] * 0.05
    
    # SMA50
    sma50 = np.mean(close[-50:]) if len(close) >= 50 else close[-1]
    
    return {
        'rsi': rsi,
        'macd': macd.iloc[-1],
        'signal': signal.iloc[-1],
        'atr': atr,
        'close': close[-1],
        'sma50': sma50
    }

def get_fundamentals(ticker):
    try:
        info = yf.Ticker(ticker).info
        return info.get('trailingPE', 999), info.get('priceToBook', 999), info.get('sector', 'Genel')
    except:
        return 999, 999, 'Genel'

def generate_ai_comment(rsi, macd, signal, price, sma50):
    comments = []
    if rsi > 70: comments.append("⚠️ RSI aşırı alımda.")
    elif rsi < 30: comments.append("✅ RSI aşırı satımda.")
    else: comments.append("📊 RSI nötr.")
    
    if macd > signal: comments.append("📈 MACD alı.")
    else: comments.append("📉 MACD satı.")
    
    if price > sma50: comments.append("📈 Trend yukarı.")
    else: comments.append("📉 Trend aşağı.")
    
    return " ".join(comments)

def calculate_sl_tp(price, atr):
    sl = price - (atr * 2.5)
    tp1 = price + (atr * 3)
    tp2 = price + (atr * 6)
    return max(sl, price * 0.90), tp1, tp2

# -----------------------------------------------------------------------------
# 3. ANALİZ MOTORU (DÜZELTİLMİŞ)
# -----------------------------------------------------------------------------

def scan_market():
    tickers = get_bist100_tickers()
    candidates = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers):
        status_text.text(f"🔍 Taranıyor: {ticker} ({i+1}/{len(tickers)})")
        
        df = fetch_single_data(ticker)
        if df is None:
            progress_bar.progress((i + 1) / len(tickers))
            continue
        
        try:
            ind = calculate_indicators(df)
            pe, pb, sector = get_fundamentals(ticker)
            
            # Puanlama Sistemi
            score = 0
            if ind['rsi'] > 50 and ind['rsi'] < 70: score += 25
            if ind['macd'] > ind['signal']: score += 25
            if ind['close'] > ind['sma50']: score += 25
            if pe < 25 and pe > 0: score += 15
            if pb < 5 and pb > 0: score += 10
            
            # Filtre: Minimum 60 puan
            if score >= 60:
                sl, tp1, tp2 = calculate_sl_tp(ind['close'], ind['atr'])
                candidates.append({
                    'Hisse': ticker,
                    'Fiyat': round(ind['close'], 2),
                    'Puan': score,
                    'RSI': round(ind['rsi'], 1),
                    'F/K': round(pe, 1) if pe else 999,
                    'PD/DD': round(pb, 1) if pb else 999,
                    'Sektör': sector,
                    'Stop': round(sl, 2),
                    'TP1': round(tp1, 2),
                    'TP2': round(tp2, 2),
                    'AI': generate_ai_comment(ind['rsi'], ind['macd'], ind['signal'], ind['close'], ind['sma50'])
                })
        except Exception as e:
            continue
        
        progress_bar.progress((i + 1) / len(tickers))
    
    status_text.text("✅ Tarama Tamamlandı!")
    
    if not candidates:
        return pd.DataFrame()
    
    df = pd.DataFrame(candidates)
    return df.sort_values(by='Puan', ascending=False)

# -----------------------------------------------------------------------------
# 4. PORTFÖY YÖNETİMİ
# -----------------------------------------------------------------------------
PORTFOLIO_FILE = 'portfoy_pro.json'

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def save_portfolio(data):
    with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def delete_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        os.remove(PORTFOLIO_FILE)

# -----------------------------------------------------------------------------
# 5. GÖRSEL BİLEŞENLER (ANİMASYONLU KARTLAR)
# -----------------------------------------------------------------------------

def display_stock_card(stock, index):
    """Animasyonlu hisse kartı"""
    st.markdown(f"""
    <div class="stock-card" style="animation-delay: {index * 0.1}s;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin: 0; color: #00ff41;">📈 {stock['Hisse']}</h3>
            <h3 style="margin: 0; color: #ffffff;">{stock['Fiyat']:.2f} ₺</h3>
        </div>
        <div style="display: flex; gap: 15px; margin: 10px 0; flex-wrap: wrap;">
            <span style="background: #374151; padding: 5px 10px; border-radius: 5px;">Puan: <b style="color: #00ff41;">{stock['Puan']}</b></span>
            <span style="background: #374151; padding: 5px 10px; border-radius: 5px;">RSI: <b>{stock['RSI']}</b></span>
            <span style="background: #374151; padding: 5px 10px; border-radius: 5px;">F/K: <b>{stock['F/K']}</b></span>
            <span style="background: #374151; padding: 5px 10px; border-radius: 5px;">Sektör: <b>{stock['Sektör']}</b></span>
        </div>
        <div class="sl-box">
            🛑 <b>Stop-Loss:</b> {stock['Stop']:.2f} ₺
        </div>
        <div class="tp-box">
            ✅ <b>TP1:</b> {stock['TP1']:.2f} ₺ &nbsp;|&nbsp; 
            ✅ <b>TP2:</b> {stock['TP2']:.2f} ₺
        </div>
        <div class="ai-box">
            🤖 <b>AI Yorumu:</b> {stock['AI']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. ANA UYGULAMA
# -----------------------------------------------------------------------------
def main():
    st.title("🚀 BIST PRO v4")
    st.markdown("### 🇹🇷 AI Destekli | 100 Hisse | Stop-Loss | Animasyonlu")
    st.info("⚠️ Yatırım Tavsiyesi Değildir. Veriler 15 dk gecikmeli olabilir.")
    
    st.divider()
    
    st.sidebar.header("⚙️ Menü")
    page = st.sidebar.radio("Sayfa", ["💼 Portföy", "🏆 Piyasa Tarama", "📊 Performans"])
    
    current_date = datetime.now()
    portfolio = load_portfolio()
    days_left = 0
    is_locked = False
    
    if portfolio:
        try:
            start_date = datetime.strptime(portfolio['start_date'], '%Y-%m-%d')
            days_left = 30 - (current_date - start_date).days
            if days_left > 0:
                is_locked = True
        except:
            pass
    
    # --- PORTFÖY SAYFASI ---
    if page == "💼 Portföy":
        c1, c2, c3 = st.columns(3)
        c1.metric("Durum", "🔒 KİLİTLİ" if is_locked else "✅ AÇIK")
        c2.metric("Kalan Gün", max(0, days_left))
        c3.metric("Hisse Sayısı", len(portfolio.get('stocks', [])) if portfolio else 0)
        
        st.divider()
        
        if not is_locked:
            st.subheader("🔍 Yeni Portföy Oluştur")
            st.write("100 hisse taranacak, en iyi 5'i seçilecek ve 30 gün kilitlenecek.")
            
            if st.button("🚀 PİYASAYI TARA VE PORTFÖY OLUŞTUR"):
                with st.spinner('⏳ 100 Hisse analiz ediliyor... (2-3 dakika)'):
                    df = scan_market()
                    
                    if not df.empty:
                        top5 = df.head(5).to_dict(orient='records')
                        save_portfolio({
                            'start_date': current_date.strftime('%Y-%m-%d'),
                            'stocks': top5
                        })
                        st.success("🎉 Portföy başarıyla oluşturuldu!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("⚠️ Şu an filtrelere uygun hisse bulunamadı. Piyasa koşulları elverişsiz olabilir.")
        else:
            st.subheader("🔒 Aktif Portföyünüz")
            stocks = portfolio.get('stocks', [])
            
            if stocks:
                for i, stock in enumerate(stocks):
                    display_stock_card(stock, i)
                
                # Performans Grafiği
                st.divider()
                st.subheader("📈 Portföy Grafiği")
                try:
                    tickers = [s['Hisse'] for s in stocks]
                    data = yf.download(tickers, period="1mo", progress=False)['Close']
                    fig = go.Figure()
                    for col in data.columns:
                        fig.add_trace(go.Scatter(x=data.index, y=data[col], name=col, line=dict(width=2)))
                    fig.update_layout(
                        template='plotly_dark',
                        title="Portföy Performansı (Son 1 Ay)",
                        xaxis_title="Tarih",
                        yaxis_title="Fiyat (₺)",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("Grafik verisi yüklenemedi.")
            else:
                st.warning("Portföy boş.")
    
    # --- PİYASA TARAMA ---
    elif page == "🏆 Piyasa Tarama":
        st.subheader("🏆 Tüm Piyasa Sıralaması")
        st.write("100 hisse puanlandı. En yüksek puanlılar önde.")
        
        if st.button("🔄 Taramayı Yenile"):
            with st.spinner('⏳ 100 Hisse taranıyor...'):
                df = scan_market()
                st.session_state['market_data'] = df
                st.success(f"✅ {len(df)} hisse bulundu!")
        
        if 'market_data' in st.session_state:
            df = st.session_state['market_data']
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥 Excel Olarak İndir", csv, "bist_analiz.csv", "text/csv")
    
    # --- PERFORMANS ---
    elif page == "📊 Performans":
        st.subheader("📊 Portföy vs BIST 100")
        
        if portfolio and portfolio.get('stocks'):
            tickers = [s['Hisse'] for s in portfolio['stocks']]
            try:
                port_data = yf.download(tickers, period="3mo", progress=False)['Close']
                bist_data = yf.download("^XU100.IS", period="3mo", progress=False)['Close']
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                   subplot_titles=('Portföy Hisseleri', 'BIST 100'))
                
                for col in port_data.columns:
                    fig.add_trace(go.Scatter(x=port_data.index, y=port_data[col], name=col), row=1, col=1)
                
                fig.add_trace(go.Scatter(x=bist_data.index, y=bist_data.iloc[:, 0], name='BIST 100', line=dict(color='red', dash='dash')), row=2, col=1)
                
                fig.update_layout(template='plotly_dark', height=600, title="Karşılaştırmalı Performans")
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("Veri yüklenemedi.")
        else:
            st.warning("Aktif portföy yok.")

if __name__ == "__main__":
    main()
