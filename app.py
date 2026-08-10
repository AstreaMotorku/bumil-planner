import streamlit as st
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Bumil Planner 280 Days - V3 Pretty", page_icon="🤰", layout="wide")

# ---------- BEAUTIFUL CSS - MIMIC HTML V3 ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Caveat:wght@600;700&display=swap');

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.stApp { background: #FFF8F0; }

/* Header */
.header-wrap {
  background: white;
  border-radius: 24px;
  padding: 18px 22px;
  border: 1px solid #F0E6D8;
  box-shadow: 0 4px 20px rgba(232,165,152,0.12);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 18px;
}
.logo-title {
  font-family: 'Caveat', cursive;
  font-size: 28px;
  font-weight: 700;
  color: #3A3A3A;
  line-height: 1;
}
.logo-sub {
  font-size: 11px;
  letter-spacing: 2px;
  color: #9B8B7A;
  text-transform: uppercase;
  font-weight: 600;
}
.badge {
  background: #D9E4DD;
  color: #5A6B5E;
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #C8D9CF;
}
.badge-pink {
  background: #FFF0EE;
  color: #A66B64;
  border: 1px solid #F7D6D0;
}

/* Tabs - pill style */
div[data-testid="stTabs"] button[role="tab"] {
  border-radius: 999px !important;
  background: white !important;
  border: 1px solid #E9DDD0 !important;
  padding: 8px 18px !important;
  margin-right: 8px !important;
  font-weight: 500 !important;
  color: #6B5E55 !important;
  transition: all 0.2s;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  background: #E8A598 !important;
  color: white !important;
  border-color: #E8A598 !important;
  box-shadow: 0 4px 12px rgba(232,165,152,0.35) !important;
}

/* Cards */
.custom-card {
  background: white;
  border-radius: 24px;
  padding: 20px;
  border: 1px solid #F0E6D8;
  box-shadow: 0 4px 18px rgba(0,0,0,0.04);
  margin-bottom: 16px;
}
.card-blush { background: #FFF6F5; border-color: #F7D6D0; }
.card-sage { background: #F3F7F4; border-color: #D9E4DD; }
.card-cream { background: #FFFCF8; border-color: #F0E6D8; }

/* Buttons */
div.stButton > button {
  background: #E8A598 !important;
  color: white !important;
  border-radius: 999px !important;
  border: none !important;
  padding: 8px 20px !important;
  font-weight: 600 !important;
  box-shadow: 0 3px 10px rgba(232,165,152,0.3) !important;
}
div.stButton > button:hover { background: #D9958A !important; }

/* Inputs */
input, textarea, div[data-baseweb="select"] > div {
  border-radius: 12px !important;
}
div[data-testid="stExpander"] {
  background: white;
  border-radius: 20px;
  border: 1px solid #F0E6D8;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}
.disclaimer-box {
  background: #FFFBEB;
  border: 1px solid #FDE68A;
  border-radius: 14px;
  padding: 12px 14px;
  font-size: 11px;
  line-height: 1.5;
  color: #92400E;
}
.footer-quote {
  text-align: center;
  font-family: 'Caveat', cursive;
  font-size: 18px;
  color: #9B8B7A;
  margin: 30px 0 10px 0;
}
div[data-testid="metric-container"] {
  background: white;
  border-radius: 18px;
  padding: 14px;
  border: 1px solid #F0E6D8;
}
</style>
""", unsafe_allow_html=True)

def default_data():
    return {
        "profil": {"nama_ibu": "", "nama_ayah": "", "hpht": "", "hpl": "", "gol_darah_ibu": "", "gol_darah_ayah": "", "rs_bidan": "", "hp_dokter": "", "bb_awal": "", "tb": "", "riwayat": ""},
        "kontrol": [{"tanggal": "", "usia": "", "td": "", "bb": "", "djj": "", "usg": "", "catatan": ""} for _ in range(6)],
        "bb_ibu": [], "bb_janin": [],
        "todo": {
            "T1 - Bulan 1 (Minggu 1-4)": [("Tes pack & catat HPHT", "Pagi hari", False), ("Hitung HPL HPHT+280", "", False), ("Mulai asam folat 400-800mcg", "Setelah makan", False), ("Stop rokok/alkohol/vape", "0 toleransi", False), ("Cek obat aman bumil?", "Tanya dokter", False), ("Daftar dokter/bidan & buku KIA", "", False), ("Buat folder dokumen KK KTP BPJS", "Fotokopi 3x", False), ("Cek BPJS/asuransi", "", False), ("Tidur 7-8 jam", "Miring kiri", False), ("Air 2.3L/hari", "", False)],
            "T1 - Bulan 2 (Minggu 5-8)": [("USG pertama kantung & DJJ", "6-8 minggu", False), ("Lab darah lengkap", "Hb, HIV, HepB", False), ("Cek TSH tiroid", "", False), ("Atasi mual porsi kecil", "Biskuit bangun tidur", False), ("Beli bra hamil", "Tanpa kawat", False), ("Catat BB mingguan", "Senin pagi", False), ("Hindari sushi mentah & setengah matang", "", False), ("Prenatal yoga 15 menit", "", False)],
            "T1 - Bulan 3 (Minggu 9-13)": [("USG NT 11-13 / NIPT", "", False), ("Konsultasi hasil lab", "", False), ("Atur cuti hamil", "", False), ("Minyak anti stretch mark", "", False), ("List pertanyaan dokter T1", "", False), ("Financial plan awal", "", False), ("Bantal hamil", "", False), ("Hindari retinol & cat rambut keras", "", False)],
            "T2 - Bulan 4 (14-17)": [("USG anatomi awal", "", False), ("Kalsium 1000mg & zat besi 27mg", "Jika saran dokter", False), ("Kelas hamil", "", False), ("Skincare bumil-friendly", "No retinol", False), ("Tidur miring kiri", "", False), ("Baju hamil 2-3 stel", "", False), ("Jalan 20-30 menit", "", False), ("Ngobrol dengan janin", "", False)],
            "T2 - Bulan 5 (18-22)": [("USG anomali detail 20 minggu WAJIB", "", False), ("Cek Hb & gula puasa", "", False), ("Catat gerakan janin", "Quickening", False), ("Riset pompa ASI & bouncer", "", False), ("Brainstorm 10 nama bayi", "", False), ("Moodboard kamar bayi", "", False), ("Planning foto maternity", "", False)],
            "T2 - Bulan 6 (23-27)": [("TTGO 24-28 minggu", "", False), ("Vaksin Tdap & flu", "Konsul dokter", False), ("Cek plasenta", "", False), ("Senam kegel 3x10", "", False), ("Edukasi ASI", "", False), ("Draft birth plan", "", False), ("Cicil perlengkapan WAJIB 50%", "", False)],
            "T3 - Bulan 7 (28-31)": [("USG pertumbuhan & doppler", "", False), ("Cek posisi kepala", "", False), ("Packing tas RS 70%", "", False), ("Kelas napas & hypnobirthing", "", False), ("Berkas KTP KK buku nikah BPJS", "Map khusus", False), ("Beli gendongan SSC", "", False), ("Finalisasi cuti", "", False)],
            "T3 - Bulan 8 (32-36)": [("Kontrol 2 mingguan", "", False), ("CTG & cek preeklamsia", "", False), ("Finalisasi kamar & cuci baju bayi", "", False), ("Belajar mandikan bedong gendong", "", False), ("Sterilisasi botol", "", False), ("Kontak darurat RS bidan driver", "Tempel kulkas", False), ("Pengaman rumah", "", False)],
            "T3 - Bulan 9 (37-40)": [("Kontrol mingguan", "", False), ("Cek panggul", "", False), ("Packing tas RS 100%", "Baju ibu 3 bayi 5 dokumen", False), ("Perineal massage", "", False), ("Latihan napas 4-7-8", "", False), ("Siaga tanda persalinan 5-1-1", "", False), ("Rute tercepat RS", "", False), ("Afirmasi positif", "", False), ("Stok frozen food", "", False)],
        },
        "newborn": {
            "WAJIB PUNYA": [
                {"nama": "Popok kain 12pcs", "qty": 12, "harga": 0, "link": "", "ket": "Katun lembut", "done": False},
                {"nama": "Popok NB 1 pack", "qty": 1, "harga": 0, "link": "", "ket": "MamyPoko", "done": False},
                {"nama": "Baju pendek 6 stel", "qty": 6, "harga": 0, "link": "", "ket": "Katun bambu", "done": False},
                {"nama": "Bedong 6 + Perlak 2", "qty": 1, "harga": 0, "link": "", "ket": "120x120 Waterproof", "done": False},
                {"nama": "Handuk 2 + Bak mandi lipat", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False},
                {"nama": "Sabun 2in1 + telon + cream ruam", "qty": 1, "harga": 0, "link": "", "ket": "Zwitsal", "done": False},
            ],
            "LUMAYAN PENTING": [
                {"nama": "Pompa ASI elektrik", "qty": 1, "harga": 0, "link": "", "ket": "Spectra", "done": False},
                {"nama": "Sterilizer UV", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False},
                {"nama": "Bouncer + Diaper bag", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False},
                {"nama": "Gendongan SSC", "qty": 1, "harga": 0, "link": "", "ket": "CuddleMe", "done": False},
            ],
            "TIDAK URGENT": [
                {"nama": "Sepatu bayi 0-3 bln", "qty": 2, "harga": 0, "link": "", "ket": "", "done": False},
                {"nama": "Stroller cabin + Car seat", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False},
            ]
        },
        "budget": [
            {"kategori": "Kontrol/USG", "nama": "USG + dokter", "estimasi": 500000, "aktual": 0, "lunas": False},
            {"kategori": "Vitamin", "nama": "Vitamin 9 bulan", "estimasi": 1500000, "aktual": 0, "lunas": False},
            {"kategori": "Bayi", "nama": "Perlengkapan wajib", "estimasi": 3000000, "aktual": 0, "lunas": False},
            {"kategori": "Lahiran", "nama": "Biaya lahiran", "estimasi": 10000000, "aktual": 0, "lunas": False},
        ],
        "faq_tracker": []
    }

LOCAL_FILE = "bumil_data.json"
def load_local():
    if os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return default_data()
    return default_data()
def save_local(data):
    with open(LOCAL_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

def get_gsheet_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_info = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        return gspread.authorize(creds)
    except: return None

def load_from_gsheet():
    try:
        client = get_gsheet_client()
        if not client: return None
        sheet_url = st.secrets["sheet_url"]
        sh = client.open_by_url(sheet_url)
        try: ws = sh.worksheet("bumil_data")
        except: ws = sh.add_worksheet(title="bumil_data", rows="1000", cols="20")
        val = ws.acell("A1").value
        if val and len(val) > 10: return json.loads(val)
        else: return default_data()
    except: return None

def save_all_gsheet(data):
    try:
        client = get_gsheet_client()
        if not client:
            save_local(data); return False
        sheet_url = st.secrets["sheet_url"]
        sh = client.open_by_url(sheet_url)
        try: ws = sh.worksheet("bumil_data")
        except: ws = sh.add_worksheet(title="bumil_data", rows="1000", cols="20")
        ws.update_acell("A1", json.dumps(data, ensure_ascii=False))
        save_local(data)
        return True
    except: save_local(data); return False

def save_all():
    data = st.session_state.data
    if st.session_state.get("use_gsheet"):
        if save_all_gsheet(data): st.toast("✅ Tersimpan ke Cloud (Google Sheets)")
        else: st.toast("Tersimpan lokal")
    else:
        save_local(data); st.toast("✅ Tersimpan lokal")

if "data" not in st.session_state:
    if "gcp_service_account" in st.secrets and "sheet_url" in st.secrets:
        st.session_state.use_gsheet = True
        gdata = load_from_gsheet()
        st.session_state.data = gdata if gdata else load_local()
    else:
        st.session_state.use_gsheet = False
        st.session_state.data = load_local()

data = st.session_state.data

# HEADER PRETTY
st.markdown("""
<div class="header-wrap">
  <div>
    <div class="logo-title">Bumil Planner 🤰</div>
    <div class="logo-sub">280 Days — DIY Edition • Handmade with love</div>
  </div>
  <div style="display:flex; gap:8px; flex-wrap:wrap;">
    <span class="badge">✨ Handmade with love</span>
    <span class="badge" style="background:#FFF0EE; color:#A66B64; border-color:#F7D6D0;">💕 280 Hari Menuju Pelukan Pertama</span>
  </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.use_gsheet:
    st.markdown('<div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:12px; padding:10px 14px; font-size:13px; color:#065F46; margin-bottom:14px;">✅ <b>Mode Cloud Aktif</b> — Data di Google Sheets, bisa edit bareng istri. Isi malem ini, besok masih ada.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:12px; padding:10px 14px; font-size:13px; color:#92400E; margin-bottom:14px;">⚠️ <b>Mode Lokal</b> — Setting Google Sheets biar permanen di Cloud.</div>', unsafe_allow_html=True)

tabs = st.tabs(["👤 Profil", "🩺 Kontrol", "✅ To-Do Detail", "👶 Newborn List", "💰 Budget", "💊 Vitamin", "❓ Dokter + AI"])

with tabs[0]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### 👤 Profil Ibu & Ayah")
    c1,c2 = st.columns(2)
    with c1:
        data["profil"]["nama_ibu"] = st.text_input("Nama Ibu", value=data["profil"]["nama_ibu"], placeholder="Mama hebat")
        data["profil"]["nama_ayah"] = st.text_input("Nama Ayah", value=data["profil"]["nama_ayah"])
        data["profil"]["hpht"] = st.text_input("HPHT (YYYY-MM-DD)", value=data["profil"]["hpht"], placeholder="2025-08-01")
        if data["profil"]["hpht"]:
            try:
                hpht = datetime.strptime(data["profil"]["hpht"], "%Y-%m-%d")
                hpl = hpht + timedelta(days=280)
                sisa = (hpl - datetime.now()).days
                st.markdown(f'<div style="background:#F3F7F4; border-radius:12px; padding:12px; margin:8px 0;"><b>HPL:</b> {hpl.strftime("%d %B %Y")} <br><small>{sisa} hari lagi 💕</small></div>', unsafe_allow_html=True)
                data["profil"]["hpl"] = hpl.strftime("%Y-%m-%d")
            except: st.caption("Format YYYY-MM-DD")
        data["profil"]["bb_awal"] = st.text_input("BB sebelum hamil (kg)", value=data["profil"]["bb_awal"])
        data["profil"]["tb"] = st.text_input("TB (cm)", value=data["profil"]["tb"])
    with c2:
        data["profil"]["gol_darah_ibu"] = st.text_input("Gol Darah Ibu", value=data["profil"]["gol_darah_ibu"])
        data["profil"]["rs_bidan"] = st.text_input("RS / Bidan", value=data["profil"]["rs_bidan"])
        data["profil"]["hp_dokter"] = st.text_input("HP Dokter", value=data["profil"]["hp_dokter"])
        data["profil"]["riwayat"] = st.text_area("Riwayat alergi / penyakit", value=data["profil"]["riwayat"])
    if st.button("💾 Simpan Profil", key="save_profil"):
        save_all()
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### 🩺 Catatan Kontrol & USG")
    for i, row in enumerate(data["kontrol"]):
        with st.expander(f"🤍 Kontrol {i+1} - {row['tanggal'] or 'Belum diisi'}", expanded=(i==0)):
            c1,c2,c3,c4 = st.columns(4)
            row["tanggal"] = c1.text_input(f"Tanggal", value=row["tanggal"], key=f"tgl_{i}")
            row["usia"] = c2.text_input(f"Usia minggu", value=row["usia"], key=f"usia_{i}")
            row["td"] = c3.text_input(f"TD", value=row["td"], key=f"td_{i}")
            row["bb"] = c4.text_input(f"BB", value=row["bb"], key=f"bb_{i}")
            row["usg"] = st.text_area(f"Hasil USG & Catatan", value=row["usg"], key=f"usg_{i}")
    if st.button("💾 Simpan Kontrol"): save_all()
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown("#### ✅ To-Do List Super Lengkap - Per Bulan & Minggu")
    for bulan, tasks in data["todo"].items():
        selesai = len([t for t in tasks if t[2]])
        total = len(tasks)
        icon = "🌱" if "T1" in bulan else "🌸" if "T2" in bulan else "🌙"
        with st.expander(f"{icon} {bulan} — {selesai}/{total} selesai"):
            for idx, (nama, ket, done) in enumerate(tasks):
                cols = st.columns([0.07, 0.93])
                checked = cols[0].checkbox("", value=done, key=f"{bulan}_{idx}")
                with cols[1]:
                    if checked: st.markdown(f"~~**{nama}**~~  \n<small style='color:#9B8B7A'>{ket}</small>")
                    else: st.markdown(f"**{nama}**  \n<small style='color:#9B8B7A'>{ket}</small>")
                if checked != done:
                    data["todo"][bulan][idx] = (nama, ket, checked)
                    save_all()
            c1,c2 = st.columns([0.8,0.2])
            new_t = c1.text_input(f"Tugas baru {bulan}", key=f"new_{bulan}", placeholder="Tugas baru...", label_visibility="collapsed")
            if c2.button(f"+ Tambah", key=f"btn_{bulan}") and new_t:
                data["todo"][bulan].append((new_t, "Custom", False))
                save_all(); st.rerun()
    st.markdown('<div class="footer-quote" style="text-align:center; font-family:Caveat; font-size:18px; color:#9B8B7A; margin-top:20px;">"Setiap tendangan kecil adalah cerita besar" 🌸</div>', unsafe_allow_html=True)

with tabs[3]:
    st.markdown("#### 👶 Newborn List by Prioritas — Harga & Link")
    cols = st.columns(3)
    for col_idx, kat in enumerate(["WAJIB PUNYA", "LUMAYAN PENTING", "TIDAK URGENT"]):
        with cols[col_idx]:
            bg = "#FFF6F5" if kat=="WAJIB PUNYA" else "#F3F7F4" if kat=="LUMAYAN PENTING" else "#FFFCF8"
            st.markdown(f'<div style="background:{bg}; border-radius:16px; padding:12px; border:1px solid #F0E6D8; margin-bottom:10px; text-align:center;"><b>{kat}</b></div>', unsafe_allow_html=True)
            total = 0
            for i, item in enumerate(data["newborn"][kat]):
                with st.container(border=True):
                    c1,c2 = st.columns([0.85,0.15])
                    item["done"] = c1.checkbox(item["nama"], value=item["done"], key=f"{kat}_{i}_done")
                    if c2.button("✕", key=f"del_{kat}_{i}"):
                        data["newborn"][kat].pop(i); save_all(); st.rerun()
                    item["qty"] = st.number_input("Qty", 1, 100, item["qty"], key=f"{kat}_{i}_qty", label_visibility="collapsed")
                    c3,c4 = st.columns(2)
                    item["harga"] = c3.number_input("Harga Rp", 0, 10000000, item["harga"], key=f"{kat}_{i}_harga")
                    item["link"] = c4.text_input("Link", value=item["link"], key=f"{kat}_{i}_link", placeholder="Shopee", label_visibility="collapsed")
                    if item["link"]: st.link_button("🔗 Buka", item["link"])
                    item["ket"] = st.text_input("Ket", value=item["ket"], key=f"{kat}_{i}_ket", placeholder="Merk", label_visibility="collapsed")
                    total += item["harga"]*item["qty"]
            st.metric(f"Total {kat}", f"Rp {total:,}")
    if st.button("💾 Simpan Newborn List"): save_all()

with tabs[4]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### 💰 Budget Prioritas")
    edited = st.data_editor(data["budget"], num_rows="dynamic", use_container_width=True, key="budget_pretty")
    if st.button("💾 Simpan Budget"):
        data["budget"] = edited; save_all()
    total_est = sum([b.get("estimasi",0) for b in data["budget"]])
    total_akt = sum([b.get("aktual",0) for b in data["budget"]])
    c1,c2,c3 = st.columns(3)
    c1.metric("Estimasi", f"Rp {total_est:,}")
    c2.metric("Aktual", f"Rp {total_akt:,}")
    c3.metric("Sisa", f"Rp {total_est-total_akt:,}")
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[5]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### 💊 Vitamin & Nutrisi Super Detail")
    st.markdown('<div class="disclaimer-box">💡 Info umum, bukan resep pribadi. Konsul dokter untuk dosis personal.</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("**🌿 WAJIB**\n- Protein 60-80gr: telur matang, ayam, lele/salmon, tempe\n- Zat Besi+Vit C: hati ayam 1x/mgg max, daging merah, bayam+jeruk\n- Kalsium 1000mg: susu hamil 2 gelas\n- Serat: pepaya matang, pisang, oat\n- Air 2.3-2.5L")
    with c2:
        st.markdown("**⛔ Hindari**\n- Sushi mentah, daging/telur setengah matang\n- Susu mentah, keju lunak tidak pasteurisasi\n- Ikan merkuri tinggi: Hiu, Todak, King Mackerel\n- Kafein >200mg, Alkohol 0, Rokok 0\n- Jamu tidak jelas")
    st.divider()
    t1,t2,t3 = st.columns(3)
    with t1: st.markdown('<div class="custom-card" style="background:#F3F7F4"><b>T1 (0-13)</b><br><small>Folat 400-800mcg pagi<br>Vit D 600 IU<br>B6 jika mual (resep dr)</small></div>', unsafe_allow_html=True)
    with t2: st.markdown('<div class="custom-card" style="background:#FFF6F5"><b>T2 (14-27)</b><br><small>Ca 1000mg malam<br>Fe 27mg malam+Vit C<br>DHA 200-300mg siang</small></div>', unsafe_allow_html=True)
    with t3: st.markdown('<div class="custom-card" style="background:#FFFCF8"><b>T3 (28-40)</b><br><small>Lanjut Fe+Ca+DHA<br>Vit K akhir jika saran<br>Mg untuk tidur</small></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[6]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### ❓ Dokter + AI - FAQ Lengkap")
    st.markdown('<div class="disclaimer-box">⚠️ <b>DISCLAIMER:</b> AI hanya info UMUM & EDUKASI, bukan diagnosis. Untuk kepastian, WAJIB konsultasi dokter/bidan. Tanda bahaya (perdarahan banyak, ketuban pecah, gerakan &lt;10x/12jam) segera ke IGD.</div>', unsafe_allow_html=True)
    sub1, sub2 = st.tabs(["📝 Tracker", "💬 FAQ + AI Dokter"])
    with sub1:
        q = st.text_area("Pertanyaan sebelum kontrol")
        a = st.text_area("Jawaban dokter")
        tgl = st.date_input("Tanggal")
        if st.button("Simpan Q&A"):
            data["faq_tracker"].append({"q": q, "a": a, "tgl": str(tgl)})
            save_all()
        for item in reversed(data["faq_tracker"][-20:]):
            st.markdown(f'<div style="background:#FFFCF8; border:1px solid #F0E6D8; border-radius:14px; padding:12px; margin-bottom:8px;"><b>Q:</b> {item["q"]}<br><b>A:</b> {item["a"]}<br><small>{item["tgl"]}</small></div>', unsafe_allow_html=True)
    with sub2:
        with st.expander("Apakah mual berat normal?"): st.write("Normal di T1 karena hCG. Makan kecil sering, biskuit sebelum bangun. Jika >24 jam tidak bisa makan/minum, segera kontrol.")
        with st.expander("Boleh HB?"): st.write("Boleh jika tidak flek, ketuban tidak rembes, tidak plasenta previa, dokter tidak larang.")
        with st.expander("Tanda persalinan asli?"): st.write("Kontraksi 5-1-1, lendir darah, ketuban pecah banyak tidak bisa ditahan.")
        st.divider()
        st.markdown("**👩‍⚕️ Tanya AI Dokter (Jawaban Umum)**")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [{"role": "ai", "content": "Halo Bunda! 👋 Saya AI edukasi OBGYN. Tanya apa saja umum (mual, flek, vitamin, makanan, tanda lahiran). Jawaban saya info umum ya."}]
        kb = {"mual": "Mual T1 normal karena hCG. Tips: porsi kecil 5-6x, biskuit bangun tidur, jahe hangat. Jika >24 jam tidak makan/minum, kontrol.", "flek": "Flek sedikit bisa implantasi, tapi tetap kontrol. Istirahat, hindari HB.", "makanan": "Wajib protein 60-80gr, Fe+Vit C, Ca 1000mg. Hindari sushi mentah, daging setengah matang, ikan merkuri tinggi, kafein >200mg, alkohol 0.", "lahiran": "Tanda asli: 5-1-1, lendir darah, ketuban pecah. Segera ke RS jika 5-1-1, ketuban pecah, perdarahan, gerakan berkurang.", "gerakan": "Mulai 18-22 minggu halus. T3 hitung 10 gerakan/12 jam. Jika <10, segera RS."}
        def get_answer(q):
            ql=q.lower()
            for k,v in kb.items():
                if k in ql: return v+"\n\nIni info umum, untuk kepastian konsultasi dokter ya."
            return "Coba kata kunci: mual, flek, makanan, lahiran, gerakan. Ini info umum, untuk kepastian konsultasi dokter."
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.write(msg["content"])
        if prompt := st.chat_input("Ketik pertanyaan umum..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)
            ans=get_answer(prompt)
            with st.chat_message("assistant"): st.write(ans)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            data["faq_tracker"].append({"q": prompt, "a": ans, "tgl": datetime.now().strftime("%Y-%m-%d %H:%M")})
            save_all()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-quote">"Setiap tendangan kecil adalah cerita besar" 🌸<br><small style="font-family:Poppins; font-size:11px;">Bumil Planner 280 Days — DIY Edition • 2026</small></div>', unsafe_allow_html=True)
