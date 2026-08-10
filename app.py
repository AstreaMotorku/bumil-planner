import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Bumil Planner - With BB Tracker", page_icon="🤰", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Caveat:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.stApp { background: #FFF8F0; }
.header-wrap { background: white; border-radius: 24px; padding: 18px 22px; border: 1px solid #F0E6D8; box-shadow: 0 4px 20px rgba(232,165,152,0.12); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:18px; }
.badge { background: #D9E4DD; color: #5A6B5E; border-radius: 999px; padding: 6px 14px; font-size: 12px; border:1px solid #C8D9CF; }
div[data-testid="stTabs"] button[role="tab"] { border-radius: 999px !important; background: white !important; border: 1px solid #E9DDD0 !important; padding: 8px 16px !important; margin-right: 6px !important; }
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { background: #E8A598 !important; color: white !important; border-color: #E8A598 !important; }
.custom-card { background: white; border-radius: 24px; padding: 20px; border: 1px solid #F0E6D8; box-shadow: 0 4px 18px rgba(0,0,0,0.04); margin-bottom: 16px; }
.disclaimer-box { background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 14px; padding: 12px 14px; font-size: 11px; line-height: 1.5; color: #92400E; }
.info-box { background: #F3F7F4; border: 1px solid #D9E4DD; border-radius: 14px; padding: 12px 14px; font-size: 12px; color: #5A6B5E; }
</style>
""", unsafe_allow_html=True)

def default_data():
    return {
        "profil": {"nama_ibu": "", "hpht": "", "hpl": "", "bb_awal": "52", "tb": "160", "rs_bidan": "", "hp_dokter": "", "riwayat": ""},
        "kontrol": [{"tanggal": "", "usia": "", "td": "", "bb": "", "djj": "", "usg": ""} for _ in range(6)],
        "bb_ibu": [{"minggu": m, "bb": None, "kenaikan": 0.0, "status": "Normal"} for m in range(4, 41)],
        "bb_janin": [{"minggu": m, "est_bb": None, "panjang": None, "kategori": "Normal"} for m in range(20, 41)],
        "todo": {
            "T1 - Bulan 1 (Minggu 1-4)": [("Tes pack & catat HPHT", "Pagi hari", False), ("Hitung HPL HPHT+280", "", False), ("Mulai asam folat 400-800mcg", "Setelah makan", False), ("Stop rokok/alkohol/vape", "0 toleransi", False), ("Cek obat aman bumil?", "Tanya dokter", False), ("Daftar dokter/bidan & buku KIA", "", False), ("Buat folder dokumen KK KTP BPJS", "Fotokopi 3x", False), ("Cek BPJS/asuransi", "", False), ("Tidur 7-8 jam", "Miring kiri", False), ("Air 2.3L/hari", "", False)],
            "T1 - Bulan 2 (Minggu 5-8)": [("USG pertama kantung & DJJ", "6-8 minggu", False), ("Lab darah lengkap", "Hb, HIV, HepB", False), ("Cek TSH tiroid", "", False), ("Atasi mual porsi kecil", "Biskuit bangun tidur", False), ("Beli bra hamil", "Tanpa kawat", False), ("Catat BB mingguan", "Senin pagi", False), ("Hindari sushi mentah", "", False), ("Prenatal yoga 15 menit", "", False)],
            "T1 - Bulan 3 (Minggu 9-13)": [("USG NT 11-13 / NIPT", "", False), ("Konsultasi hasil lab", "", False), ("Atur cuti hamil", "", False), ("Minyak anti stretch mark", "", False), ("List pertanyaan dokter T1", "", False), ("Financial plan awal", "", False), ("Bantal hamil", "", False), ("Hindari retinol", "", False)],
            "T2 - Bulan 4 (14-17)": [("USG anatomi awal", "", False), ("Kalsium 1000mg & zat besi 27mg", "Jika saran dokter", False), ("Kelas hamil", "", False), ("Skincare bumil-friendly", "No retinol", False), ("Tidur miring kiri", "", False), ("Baju hamil 2-3 stel", "", False), ("Jalan 20-30 menit", "", False), ("Ngobrol dengan janin", "", False)],
            "T2 - Bulan 5 (18-22)": [("USG anomali detail 20 minggu WAJIB", "", False), ("Cek Hb & gula puasa", "", False), ("Catat gerakan janin", "Quickening", False), ("Riset pompa ASI & bouncer", "", False), ("Brainstorm 10 nama bayi", "", False), ("Moodboard kamar bayi", "", False), ("Planning foto maternity", "", False)],
            "T2 - Bulan 6 (23-27)": [("TTGO 24-28 minggu", "", False), ("Vaksin Tdap & flu", "Konsul dokter", False), ("Cek plasenta", "", False), ("Senam kegel 3x10", "", False), ("Edukasi ASI", "", False), ("Draft birth plan", "", False), ("Cicil perlengkapan WAJIB 50%", "", False)],
            "T3 - Bulan 7 (28-31)": [("USG pertumbuhan & doppler", "", False), ("Cek posisi kepala", "", False), ("Packing tas RS 70%", "", False), ("Kelas napas & hypnobirthing", "", False), ("Berkas KTP KK buku nikah BPJS", "Map khusus", False), ("Beli gendongan SSC", "", False), ("Finalisasi cuti", "", False)],
            "T3 - Bulan 8 (32-36)": [("Kontrol 2 mingguan", "", False), ("CTG & cek preeklamsia", "", False), ("Finalisasi kamar & cuci baju bayi", "", False), ("Belajar mandikan bedong gendong", "", False), ("Sterilisasi botol", "", False), ("Kontak darurat RS bidan driver", "Tempel kulkas", False), ("Pengaman rumah", "", False)],
            "T3 - Bulan 9 (37-40)": [("Kontrol mingguan", "", False), ("Cek panggul", "", False), ("Packing tas RS 100%", "Baju ibu 3 bayi 5 dokumen", False), ("Perineal massage", "", False), ("Latihan napas 4-7-8", "", False), ("Siaga tanda persalinan 5-1-1", "", False), ("Rute tercepat RS", "", False), ("Afirmasi positif", "", False), ("Stok frozen food", "", False)],
        },
        "newborn": {
            "WAJIB PUNYA": [{"nama": "Popok kain 12pcs + Perlak 2", "qty": 1, "harga": 0, "link": "", "ket": "Katun", "done": False}],
            "LUMAYAN PENTING": [{"nama": "Pompa ASI elektrik", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False}],
            "TIDAK URGENT": [{"nama": "Stroller + Car seat", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False}]
        },
        "budget": [{"kategori": "Kontrol/USG", "nama": "USG + dokter", "estimasi": 500000, "aktual": 0, "lunas": False}],
        "faq_tracker": []
    }

LOCAL_FILE = "bumil_data.json"
def load_local():
    if os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if "bb_ibu" not in loaded or not loaded["bb_ibu"] or len(loaded["bb_ibu"]) < 10:
                    loaded["bb_ibu"] = default_data()["bb_ibu"]
                if "bb_janin" not in loaded or not loaded["bb_janin"] or len(loaded["bb_janin"]) < 10:
                    loaded["bb_janin"] = default_data()["bb_janin"]
                return loaded
        except:
            return default_data()
    return default_data()

def save_local(data):
    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_gsheet_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_info = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        return gspread.authorize(creds)
    except:
        return None

def load_from_gsheet():
    try:
        client = get_gsheet_client()
        if not client: return None
        sh = client.open_by_url(st.secrets["sheet_url"])
        try: ws = sh.worksheet("bumil_data")
        except: ws = sh.add_worksheet(title="bumil_data", rows="1000", cols="20")
        val = ws.acell("A1").value
        if val and len(val) > 10:
            loaded = json.loads(val)
            if "bb_ibu" not in loaded or not loaded["bb_ibu"]: loaded["bb_ibu"] = default_data()["bb_ibu"]
            if "bb_janin" not in loaded or not loaded["bb_janin"]: loaded["bb_janin"] = default_data()["bb_janin"]
            return loaded
        else:
            return default_data()
    except:
        return None

def save_all_gsheet(data):
    try:
        client = get_gsheet_client()
        if not client:
            save_local(data); return False
        sh = client.open_by_url(st.secrets["sheet_url"])
        try: ws = sh.worksheet("bumil_data")
        except: ws = sh.add_worksheet(title="bumil_data", rows="1000", cols="20")
        ws.update_acell("A1", json.dumps(data, ensure_ascii=False))
        save_local(data)
        return True
    except:
        save_local(data); return False

def save_all():
    data = st.session_state.data
    if st.session_state.get("use_gsheet"):
        if save_all_gsheet(data): st.toast("✅ Tersimpan ke Cloud")
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

st.markdown("""
<div class="header-wrap">
  <div><div style="font-family:Caveat; font-size:26px; font-weight:700;">Bumil Planner 280 DAYS - DIY EDITION 🤰</div><div style="font-size:11px; color:#9B8B7A;">Super Detail • 280 Hari • V2 Super Detail + BB Tracker</div></div>
  <div style="display:flex; gap:8px;"><span class="badge">V2 Super Detail</span><span style="background:#FFF0EE; color:#A66B64; border-radius:999px; padding:6px 14px; font-size:12px; border:1px solid #F7D6D0;">No Print</span></div>
</div>
""", unsafe_allow_html=True)

if st.session_state.use_gsheet:
    st.success("✅ Mode Cloud Aktif — BB Tracker di Google Sheets, bisa edit bareng")
else:
    st.warning("⚠️ Mode Lokal")

tabs = st.tabs(["👤 Profil", "🩺 Kontrol", "⚖️ BB", "✅ To-Do", "👶 Newborn", "💰 Budget", "💊 Vitamin", "❓ Dokter FAQ"])

with tabs[0]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### 👤 Profil Ibu")
    c1,c2 = st.columns(2)
    with c1:
        data["profil"]["nama_ibu"] = st.text_input("Nama Ibu", value=data["profil"]["nama_ibu"])
        data["profil"]["hpht"] = st.text_input("HPHT YYYY-MM-DD", value=data["profil"]["hpht"])
        if data["profil"]["hpht"]:
            try:
                hpht = datetime.strptime(data["profil"]["hpht"], "%Y-%m-%d")
                hpl = hpht + timedelta(days=280)
                st.info(f"HPL: {hpl.strftime('%d %B %Y')} — {(hpl - datetime.now()).days} hari lagi")
            except: pass
        data["profil"]["bb_awal"] = st.text_input("BB Awal", value=data["profil"]["bb_awal"])
        data["profil"]["tb"] = st.text_input("TB", value=data["profil"]["tb"])
    with c2:
        data["profil"]["rs_bidan"] = st.text_input("RS / Bidan", value=data["profil"]["rs_bidan"])
        data["profil"]["hp_dokter"] = st.text_input("HP Dokter", value=data["profil"]["hp_dokter"])
        data["profil"]["riwayat"] = st.text_area("Riwayat", value=data["profil"]["riwayat"])
    if st.button("💾 Simpan Profil"): save_all()
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### 🩺 Kontrol")
    for i, row in enumerate(data["kontrol"]):
        with st.expander(f"Kontrol {i+1} - {row['tanggal'] or 'Belum'}", expanded=(i==0)):
            c1,c2,c3,c4 = st.columns(4)
            row["tanggal"] = c1.text_input("Tanggal", value=row["tanggal"], key=f"tgl_{i}")
            row["usia"] = c2.text_input("Usia minggu", value=row["usia"], key=f"usia_{i}")
            row["td"] = c3.text_input("TD", value=row["td"], key=f"td_{i}")
            row["bb"] = c4.text_input("BB", value=row["bb"], key=f"bb_{i}")
            row["usg"] = st.text_area("Hasil USG", value=row["usg"], key=f"usg_{i}")
    if st.button("💾 Simpan Kontrol"): save_all()
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown("### ⚖️ BB Ibu & Janin Tracker — Persis V2 Super Detail")
    col_ibu, col_janin = st.columns(2, gap="large")
    with col_ibu:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("#### BB Ibu Tracker")
        c1,c2 = st.columns(2)
        bb_awal = c1.text_input("BB Awal", value=data["profil"]["bb_awal"], key="bb_awal_track")
        tb = c2.text_input("TB", value=data["profil"]["tb"], key="tb_track")
        data["profil"]["bb_awal"] = bb_awal
        data["profil"]["tb"] = tb
        try: bb_awal_f = float(bb_awal) if bb_awal else 52.0
        except: bb_awal_f = 52.0
        df_ibu = pd.DataFrame(data["bb_ibu"])
        df_chart = df_ibu.dropna(subset=["bb"])
        if not df_chart.empty:
            df_chart["bb"] = pd.to_numeric(df_chart["bb"], errors='coerce')
            st.line_chart(df_chart.set_index("minggu")["bb"], height=180)
        else:
            st.markdown('<div style="background:#FFF8F0; border-radius:12px; padding:40px; text-align:center; color:#9B8B7A; border:1px dashed #E9DDD0;">Isi BB untuk lihat grafik</div>', unsafe_allow_html=True)
        st.markdown("**Tabel BB Ibu Per Minggu**")
        edited_ibu = st.data_editor(
            df_ibu,
            column_config={
                "minggu": st.column_config.NumberColumn("Minggu", disabled=True),
                "bb": st.column_config.NumberColumn("BB", format="%.1f kg", min_value=30.0, max_value=150.0),
                "kenaikan": st.column_config.NumberColumn("Kenaikan", format="%.1f kg", disabled=True),
                "status": st.column_config.SelectboxColumn("Status", options=["Normal", "Kurang", "Lebih", "Perlu Perhatian"], required=True)
            },
            hide_index=True, use_container_width=True, key="edit_bb_ibu", height=400
        )
        for idx, row in edited_ibu.iterrows():
            if pd.notna(row["bb"]) and row["bb"] != "":
                try: edited_ibu.at[idx, "kenaikan"] = round(float(row["bb"]) - bb_awal_f, 1)
                except: edited_ibu.at[idx, "kenaikan"] = 0.0
            else: edited_ibu.at[idx, "kenaikan"] = 0.0
        if st.button("💾 Simpan BB Ibu"):
            data["bb_ibu"] = edited_ibu.to_dict(orient="records")
            save_all()
            st.success("BB Ibu tersimpan!")
        st.markdown('<div class="info-box"><b>Info:</b> Ideal: Kurus 12.5-18kg, Normal 11.5-16kg, Gemuk 7-11.5kg, Obesitas 5-9kg. T1 naik 1-2kg, T2-T3 0.35-0.5kg/minggu.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_janin:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("#### BB Janin Tracker")
        df_janin = pd.DataFrame(data["bb_janin"])
        df_j_chart = df_janin.dropna(subset=["est_bb"])
        if not df_j_chart.empty:
            df_j_chart["est_bb"] = pd.to_numeric(df_j_chart["est_bb"], errors='coerce')
            st.line_chart(df_j_chart.set_index("minggu")["est_bb"], height=180)
        else:
            st.markdown('<div style="background:#FFF8F0; border-radius:12px; padding:40px; text-align:center; color:#9B8B7A; border:1px dashed #E9DDD0;">Grafik BB Janin (isi untuk lihat)</div>', unsafe_allow_html=True)
        st.markdown("**Tabel BB Janin Per Minggu**")
        edited_janin = st.data_editor(
            df_janin,
            column_config={
                "minggu": st.column_config.NumberColumn("Minggu", disabled=True),
                "est_bb": st.column_config.NumberColumn("Est BB (gr)", min_value=0, max_value=6000, format="%d gr"),
                "panjang": st.column_config.NumberColumn("Panjang (cm)", min_value=0, max_value=60, format="%.1f cm"),
                "kategori": st.column_config.SelectboxColumn("Kategori", options=["Normal", "Kecil (<10p)", "Besar (>90p)", "Perlu Cek Dokter"], required=True)
            },
            hide_index=True, use_container_width=True, key="edit_bb_janin", height=400
        )
        if st.button("💾 Simpan BB Janin"):
            data["bb_janin"] = edited_janin.to_dict(orient="records")
            save_all()
            st.success("BB Janin tersimpan!")
        st.markdown('<div class="info-box" style="background:#D9E4DD;"><b>Info pertumbuhan:</b> 28w ~1000gr, 32w ~1700gr, 36w ~2600gr, 40w ~3300gr. Panjang 28w ~37cm, 40w ~51cm. Jika &lt;10 persentil atau &gt;90 persentil, konsultasi dokter untuk Doppler & nutrisi.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tabs[3]:
    st.markdown("#### ✅ To-Do List Super Lengkap")
    for bulan, tasks in data["todo"].items():
        selesai = len([t for t in tasks if t[2]])
        total = len(tasks)
        icon = "🌱" if "T1" in bulan else "🌸" if "T2" in bulan else "🌙"
        with st.expander(f"{icon} {bulan} — {selesai}/{total} selesai"):
            for idx, (nama, ket, done) in enumerate(tasks):
                c1,c2 = st.columns([0.06, 0.94])
                checked = c1.checkbox("", value=done, key=f"{bulan}_{idx}_todo", label_visibility="collapsed")
                with c2:
                    st.markdown(f"**{nama}**")
                    st.caption(ket)
                if checked != done:
                    data["todo"][bulan][idx] = (nama, ket, checked)
                    save_all()
            c1,c2 = st.columns([0.85,0.15])
            new_t = c1.text_input("Tambah", key=f"new_{bulan}", placeholder="Tugas baru...", label_visibility="collapsed")
            if c2.button("Tambah", key=f"btn_{bulan}") and new_t:
                data["todo"][bulan].append((new_t, "Custom", False))
                save_all(); st.rerun()

with tabs[4]:
    st.markdown("#### 👶 Newborn List - Checklist Belanja Bayi")
    st.caption("Tambah item baru di tiap kategori, isi harga & link Shopee, centang kalau sudah beli. Total otomatis kehitung & tersimpan di Cloud.")

    # Quick template button
    with st.expander("📦 Load Template Lengkap (V2 Super Detail) - Klik untuk isi otomatis", expanded=False):
        st.write("Kalau list kamu kosong, klik ini untuk load template lengkap biar gak ketik satu-satu")
        if st.button("✨ Load Template 15 Item Lengkap"):
            data["newborn"] = {
                "WAJIB PUNYA": [
                    {"nama": "Popok kain 12pcs + Perlak 2 lembar", "qty": 1, "harga": 0, "link": "", "ket": "Katun lembut, perlak waterproof", "done": False},
                    {"nama": "Popok sekali pakai NB 1 pack", "qty": 1, "harga": 0, "link": "", "ket": "MamyPoko / Sweety NB", "done": False},
                    {"nama": "Baju pendek 6 stel + panjang 4 stel", "qty": 1, "harga": 0, "link": "", "ket": "Katun bambu 0-3 bulan", "done": False},
                    {"nama": "Bedong kain 6 pcs + Topi kupluk 3 pcs", "qty": 1, "harga": 0, "link": "", "ket": "120x120cm", "done": False},
                    {"nama": "Handuk bayi 2 + Washlap 6 + Bak mandi lipat", "qty": 1, "harga": 0, "link": "", "ket": "Handuk lembut", "done": False},
                    {"nama": "Sabun 2in1 + Minyak telon + Cream ruam + Tisu basah", "qty": 1, "harga": 0, "link": "", "ket": "Zwitsal / Bambi / Cussons", "done": False},
                ],
                "LUMAYAN PENTING": [
                    {"nama": "Pompa ASI elektrik + Cooler bag", "qty": 1, "harga": 0, "link": "", "ket": "Spectra / MomUung", "done": False},
                    {"nama": "Sterilizer UV + Botol kaca 2 pcs", "qty": 1, "harga": 0, "link": "", "ket": "UV sterilizer", "done": False},
                    {"nama": "Bouncer + Diaper bag", "qty": 1, "harga": 0, "link": "", "ket": "Bouncer bayi", "done": False},
                    {"nama": "Gendongan SSC (CuddleMe / Ergobaby)", "qty": 1, "harga": 0, "link": "", "ket": "Gendongan depan", "done": False},
                ],
                "TIDAK URGENT": [
                    {"nama": "Sepatu bayi + Baju jalan 2 stel", "qty": 1, "harga": 0, "link": "", "ket": "Untuk jalan", "done": False},
                    {"nama": "Stroller cabin + Car seat", "qty": 1, "harga": 0, "link": "", "ket": "Bisa nanti", "done": False},
                    {"nama": "Baby box / Kasur bayi + Kelambu", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False},
                ]
            }
            save_all()
            st.success("Template loaded! Refresh halaman.")
            st.rerun()

    cols = st.columns(3)
    for col_idx, kat in enumerate(["WAJIB PUNYA", "LUMAYAN PENTING", "TIDAK URGENT"]):
        with cols[col_idx]:
            st.markdown(f"**{kat}**")
            total = 0
            for i, item in enumerate(data["newborn"][kat]):
                with st.container(border=True):
                    item["done"] = st.checkbox(item["nama"], value=item["done"], key=f"{kat}_{i}_done_nb")
                    st.caption(item.get("ket",""))
                    c_qty, c_harga = st.columns(2)
                    item["qty"] = c_qty.number_input("Qty", 1, 100, item["qty"], key=f"{kat}_{i}_qty_nb")
                    item["harga"] = c_harga.number_input("Harga Rp", 0, 10000000, item["harga"], key=f"{kat}_{i}_harga_nb")
                    item["link"] = st.text_input("Link Shopee", value=item["link"], key=f"{kat}_{i}_link_nb", placeholder="https://shopee.co.id/...")
                    if item["link"]: 
                        st.link_button("🔗 Buka Link", item["link"])
                    if st.button("✕ Hapus", key=f"del_{kat}_{i}_nb"):
                        data["newborn"][kat].pop(i); save_all(); st.rerun()
                    total += item["harga"]*item["qty"]
            st.metric(f"Total {kat}", f"Rp {total:,}")
            
            # FORM TAMBAH ITEM - INI YANG KEMARIN HILANG
            with st.expander(f"➕ Tambah Item {kat}", expanded=False):
                new_nama = st.text_input("Nama barang", key=f"new_nama_{kat}", placeholder="Contoh: Bedong 3 pcs")
                new_ket = st.text_input("Keterangan", key=f"new_ket_{kat}", placeholder="Bahan katun, ukuran 120x120")
                c1,c2 = st.columns(2)
                new_qty = c1.number_input("Qty", 1, 100, 1, key=f"new_qty_{kat}")
                new_harga = c2.number_input("Harga satuan Rp", 0, 10000000, 0, key=f"new_harga_{kat}")
                new_link = st.text_input("Link Shopee (opsional)", key=f"new_link_{kat}", placeholder="https://shopee...")
                if st.button(f"✅ Tambah ke {kat}", key=f"add_{kat}", use_container_width=True):
                    if new_nama.strip():
                        data["newborn"][kat].append({"nama": new_nama.strip(), "qty": new_qty, "harga": new_harga, "link": new_link.strip(), "ket": new_ket.strip(), "done": False})
                        save_all()
                        st.success(f"✅ {new_nama} ditambahkan!")
                        st.rerun()
                    else:
                        st.warning("Nama barang harus diisi!")

    st.divider()
    col_save, col_total = st.columns([1,2])
    if col_save.button("💾 Simpan Semua Newborn ke Cloud", use_container_width=True):
        save_all()
        st.success("Tersimpan!")
    # Grand total
    grand_total = 0
    for kat in ["WAJIB PUNYA", "LUMAYAN PENTING", "TIDAK URGENT"]:
        for item in data["newborn"][kat]:
            grand_total += item["harga"]*item["qty"]
    col_total.metric("💰 Grand Total Semua Perlengkapan", f"Rp {grand_total:,}")

with tabs[5]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### 💰 Budget")
    edited = st.data_editor(data["budget"], num_rows="dynamic", use_container_width=True, key="budget_bb")
    if st.button("Simpan Budget"):
        data["budget"] = edited; save_all()
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[6]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### 💊 Vitamin & Nutrisi Super Detail")
    st.markdown('<div class="disclaimer-box">💡 Info umum, bukan resep pribadi. Konsul dokter.</div>', unsafe_allow_html=True)
    v1,v2 = st.columns(2)
    with v1:
        st.markdown("**🌿 WAJIB**\n- Protein 60-80gr: telur matang, ayam, lele/salmon, tempe\n- Zat Besi+Vit C: hati ayam 1x/mgg max, daging merah, bayam+jeruk\n- Kalsium 1000mg: susu hamil 2 gelas\n- Serat: pepaya matang, pisang, oat\n- Air 2.3-2.5L")
    with v2:
        st.markdown("**⛔ Hindari**\n- Sushi mentah, daging/telur setengah matang\n- Susu mentah, keju lunak tidak pasteurisasi\n- Ikan merkuri tinggi: Hiu, Todak, King Mackerel\n- Kafein >200mg, Alkohol 0, Rokok 0\n- Jamu tidak jelas")
    st.divider()
    t1,t2,t3 = st.columns(3)
    with t1: st.markdown('<div class="custom-card" style="background:#F3F7F4"><b>T1 (0-13)</b><br><small>Folat 400-800mcg pagi<br>Vit D 600 IU<br>B6 jika mual (resep dr)</small></div>', unsafe_allow_html=True)
    with t2: st.markdown('<div class="custom-card" style="background:#FFF6F5"><b>T2 (14-27)</b><br><small>Ca 1000mg malam<br>Fe 27mg malam+Vit C<br>DHA 200-300mg siang</small></div>', unsafe_allow_html=True)
    with t3: st.markdown('<div class="custom-card" style="background:#FFFCF8"><b>T3 (28-40)</b><br><small>Lanjut Fe+Ca+DHA<br>Vit K akhir jika saran<br>Mg untuk tidur</small></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[7]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### ❓ Dokter + AI FAQ")
    st.markdown('<div class="disclaimer-box">⚠️ AI hanya info UMUM & EDUKASI, bukan diagnosis. Untuk kepastian, WAJIB konsultasi dokter. Tanda bahaya (perdarahan banyak, ketuban pecah, gerakan &lt;10x/12jam) segera IGD.</div>', unsafe_allow_html=True)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "ai", "content": "Halo Bunda! Saya AI edukasi OBGYN. Tanya apa saja umum (mual, flek, vitamin, makanan, tanda lahiran)."}]
    kb = {"mual": "Mual T1 normal karena hCG. Tips: porsi kecil 5-6x, biskuit bangun tidur.", "flek": "Flek sedikit bisa implantasi, tapi tetap kontrol.", "makanan": "Wajib protein 60-80gr, Fe+Vit C, Ca 1000mg. Hindari sushi mentah, setengah matang, merkuri tinggi.", "lahiran": "Tanda asli: 5-1-1, lendir darah, ketuban pecah. Segera ke RS jika 5-1-1.", "gerakan": "Mulai 18-22 minggu halus. T3 hitung 10 gerakan/12 jam. Jika <10, segera RS."}
    def get_answer(q):
        ql=q.lower()
        for k,v in kb.items():
            if k in ql: return v+"\n\nIni info umum ya."
        return "Coba kata kunci: mual, flek, makanan, lahiran, gerakan. Ini info umum, konsultasi dokter ya."
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

st.markdown('<div style="text-align:center; font-family:Caveat; font-size:18px; color:#9B8B7A; margin-top:30px;">"Setiap tendangan kecil adalah cerita besar" 🌸</div>', unsafe_allow_html=True)
