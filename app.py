import streamlit as st
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Bumil Planner 280 Days - V3 Fixed", page_icon="🤰", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Caveat:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.stApp { background: #FFF8F0; }
.header-wrap {
  background: white; border-radius: 24px; padding: 18px 22px;
  border: 1px solid #F0E6D8; box-shadow: 0 4px 20px rgba(232,165,152,0.12);
  display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 18px;
}
.logo-title { font-family: 'Caveat', cursive; font-size: 28px; font-weight: 700; color: #3A3A3A; line-height: 1; }
.logo-sub { font-size: 11px; letter-spacing: 2px; color: #9B8B7A; text-transform: uppercase; font-weight: 600; }
.badge { background: #D9E4DD; color: #5A6B5E; border-radius: 999px; padding: 6px 14px; font-size: 12px; font-weight: 500; border: 1px solid #C8D9CF; }
div[data-testid="stTabs"] button[role="tab"] {
  border-radius: 999px !important; background: white !important; border: 1px solid #E9DDD0 !important;
  padding: 8px 18px !important; margin-right: 8px !important; font-weight: 500 !important; color: #6B5E55 !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  background: #E8A598 !important; color: white !important; border-color: #E8A598 !important;
  box-shadow: 0 4px 12px rgba(232,165,152,0.35) !important;
}
.custom-card {
  background: white; border-radius: 24px; padding: 20px;
  border: 1px solid #F0E6D8; box-shadow: 0 4px 18px rgba(0,0,0,0.04); margin-bottom: 16px;
}
.disclaimer-box {
  background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 14px;
  padding: 12px 14px; font-size: 11px; line-height: 1.5; color: #92400E;
}
.vitamin-card { border-radius: 18px; padding: 16px; border: 1px solid #F0E6D8; height: 100%; }
</style>
""", unsafe_allow_html=True)

def default_data():
    return {
        "profil": {"nama_ibu": "", "nama_ayah": "", "hpht": "", "hpl": "", "gol_darah_ibu": "", "rs_bidan": "", "hp_dokter": "", "bb_awal": "", "tb": "", "riwayat": ""},
        "kontrol": [{"tanggal": "", "usia": "", "td": "", "bb": "", "djj": "", "usg": ""} for _ in range(6)],
        "todo": {
            "T1 - Bulan 1 (Minggu 1-4)": [("Tes pack & catat HPHT", "Pakai tes pagi hari, foto hasil untuk dokter", False), ("Hitung HPL = HPHT + 280 hari", "Catat di profil, ini patokan kontrol", False), ("Mulai asam folat 400-800mcg", "Tiap pagi setelah makan, cegah cacat tabung saraf", False), ("Stop total rokok / alkohol / vape", "0 toleransi alkohol, rokok = risiko BBLR", False), ("Cek semua obat yang sedang diminum aman bumil?", "Tanya dokter, jangan stop obat kronis tanpa dokter", False), ("Daftar dokter / bidan & buat buku KIA", "Simpan kontak & jadwal", False), ("Buat folder dokumen KK KTP BPJS buku nikah", "Fotokopi 3 rangkap, map khusus", False), ("Cek BPJS / asuransi aktif & faskes", "Ubah faskes jika perlu", False), ("Atur jam tidur 7-8 jam miring kiri mulai sekarang", "Tidur teratur bantu hormon", False), ("Minum air 2.3L per hari", "Bawa botol minum kemana-mana", False)],
            "T1 - Bulan 2 (Minggu 5-8)": [("USG pertama konfirmasi kantung & detak jantung", "Ideal usia 6-8 minggu, pastikan di dalam rahim", False), ("Lab darah lengkap: Hb, gol darah, HIV, sifilis, Hep B", "Puasa jika diminta, bawa suami", False), ("Cek TSH tiroid", "Penting untuk otak janin", False), ("Atasi mual: makan porsi kecil 5-6x sehari", "Biskuit / roti sebelum bangun tidur", False), ("Beli bra hamil tanpa kawat yang nyaman", "Payudara mulai nyeri & membesar", False), ("Mulai catat BB mingguan setiap Senin pagi", "Pakai timbangan sama", False), ("Hindari total sushi mentah, daging setengah matang, telur setengah matang", "Risiko toksoplasma & listeria", False), ("Daftar prenatal yoga ringan 15 menit", "Youtube: yoga bumil trimester 1", False)],
            "T1 - Bulan 3 (Minggu 9-13)": [("USG NT 11-13 minggu / NIPT optional", "Screening kelainan kromosom", False), ("Konsultasi hasil lab dengan dokter", "Bawa semua hasil", False), ("Atur cuti hamil di kantor & lapor HR", "Siapkan handover plan", False), ("Mulai pakai minyak anti stretch mark", "Bio oil / coconut oil / strech mark cream", False), ("Buat list 10 pertanyaan dokter T1", "Tulis di tab Dokter", False), ("Buat financial plan awal & tabungan lahiran", "Estimasi 15-30jt tergantung RS", False), ("Beli bantal hamil kecil untuk pinggang", "", False), ("Hindari skincare retinol, hydroquinone, formalin & cat rambut kimia keras", "Ganti ke bumil-friendly", False)],
            "T2 - Bulan 4 (Minggu 14-17)": [("USG anatomi awal", "Cek perkembangan organ", False), ("Mulai kalsium 1000mg malam & zat besi 27mg jika saran dokter", "Minum jauh dari susu & kopi", False), ("Ikut kelas hamil online/offline", "Kelas napas, nutrisi", False), ("Ganti skincare ke bumil-friendly", "Cek ingredients di cekbpom", False), ("Biasakan tidur miring kiri pakai bantal", "Aliran darah ke janin lebih baik", False), ("Beli baju hamil 2-3 stel bahan katun adem", "", False), ("Jalan kaki 20-30 menit tiap hari", "Hindari lari / lompat", False), ("Mulai ajak ngobrol & putar musik untuk janin", "Janin mulai dengar", False)],
            "T2 - Bulan 5 (Minggu 18-22)": [("USG anomali detail 18-22 minggu WAJIB", "Cek lengkap organ, jari, jantung", False), ("Cek Hb & gula darah puasa", "Deteksi anemia & diabetes gestasional", False), ("Mulai catat gerakan janin halus (quickening)", "Seperti kupu-kupu / gelembung", False), ("Riset pompa ASI elektrik/manual & bouncer", "Baca review", False), ("Brainstorm 10 nama bayi laki & perempuan", "Diskusi dengan suami", False), ("Bikin moodboard kamar bayi", "Pinterest / Instagram", False), ("Planning foto maternity & baju", "Ideal 28-32 minggu", False)],
            "T2 - Bulan 6 (Minggu 23-27)": [("Tes toleransi glukosa TTGO 24-28 minggu", "Minum larutan gula, bawa bekal", False), ("Vaksin Tdap & flu (konsul dokter)", "Penting untuk kekebalan bayi", False), ("Cek posisi plasenta", "Plasenta previa / tidak", False), ("Senam kegel 3x10 tiap hari", "Cegah ngompol & bantu persalinan", False), ("Edukasi ASI & pelekatan yang benar", "Ikut kelas laktasi", False), ("Draft birth plan: normal/SC, IMD, siapa dampingi", "Tulis & print", False), ("Cicil perlengkapan WAJIB PUNYA 50%", "Jangan kalap", False)],
            "T3 - Bulan 7 (Minggu 28-31)": [("USG pertumbuhan & doppler", "Cek BB janin & aliran darah", False), ("Cek posisi kepala janin", "Sudah di bawah / sungsang", False), ("Packing tas RS 70%", "List di tab Newborn", False), ("Kelas napas persalinan & hypnobirthing", "Latihan napas 4-7-8", False), ("Siapkan berkas KTP KK buku nikah BPJS materai 10rb", "Masuk map khusus siap bawa", False), ("Beli & cuci gendongan SSC & car seat riset", "Coba dulu", False), ("Finalisasi cuti melahirkan & handover kerjaan", "", False)],
            "T3 - Bulan 8 (Minggu 32-36)": [("Kontrol 2 mingguan + CTG", "Cek detak & kontraksi", False), ("Cek tanda bahaya preeklamsia: tensi, bengkak, protein urine", "", False), ("Finalisasi kamar & cuci semua baju bayi dengan detergen khusus bayi", "Cuci tanpa pewangi", False), ("Belajar mandikan, bedong, gendong, sendawakan dari Youtube bidan", "", False), ("Sterilisasi botol & pompa ASI", "Rebus / UV", False), ("Siapkan kontak darurat: RS, bidan, driver, keluarga", "Tempel di kulkas & HP", False), ("Instal pengaman rumah: tutup stopkontak, anti slip, pagar", "", False)],
            "T3 - Bulan 9 (Minggu 37-40)": [("Kontrol mingguan", "Cek pembukaan & panggul", False), ("Cek jalan lahir", "", False), ("Packing tas RS 100%: baju ibu 3, bayi 5, pembalut nifas, dokumen, charger, camilan", "Taruh di dekat pintu", False), ("Perineal massage tiap malam dengan minyak kelapa", "Cegah robekan", False), ("Latihan napas mengejan 4-7-8 & posisi mengejan", "", False), ("Siaga tanda persalinan: lendir darah, ketuban pecah, kontraksi 5-1-1", "Hafal 5-1-1", False), ("Cek rute tercepat ke RS & plan B jika macet", "Simulasi", False), ("Afirmasi positif & mental ready, curhat dengan suami", "", False), ("Stok frozen food & kebutuhan rumah 2 minggu", "Biar suami gak panik", False)],
        },
        "newborn": {
            "WAJIB PUNYA": [
                {"nama": "Popok kain 12pcs + Perlak 2", "qty": 1, "harga": 0, "link": "", "ket": "Katun lembut", "done": False},
                {"nama": "Popok NB 1 pack + Tisu basah", "qty": 1, "harga": 0, "link": "", "ket": "MamyPoko", "done": False},
                {"nama": "Baju pendek 6 + panjang 4 + Bedong 6", "qty": 1, "harga": 0, "link": "", "ket": "Katun bambu", "done": False},
                {"nama": "Handuk 2 + Washlap 6 + Bak mandi lipat", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False},
            ],
            "LUMAYAN PENTING": [
                {"nama": "Pompa ASI elektrik + Cooler bag", "qty": 1, "harga": 0, "link": "", "ket": "Spectra", "done": False},
                {"nama": "Sterilizer UV + Bouncer", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False},
                {"nama": "Diaper bag + Gendongan SSC", "qty": 1, "harga": 0, "link": "", "ket": "CuddleMe", "done": False},
            ],
            "TIDAK URGENT": [
                {"nama": "Sepatu + Baju jalan", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False},
                {"nama": "Stroller + Car seat", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False},
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
        sh = client.open_by_url(st.secrets["sheet_url"])
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
        sh = client.open_by_url(st.secrets["sheet_url"])
        try: ws = sh.worksheet("bumil_data")
        except: ws = sh.add_worksheet(title="bumil_data", rows="1000", cols="20")
        ws.update_acell("A1", json.dumps(data, ensure_ascii=False))
        save_local(data)
        return True
    except: save_local(data); return False

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
<div style="background:white; border-radius:24px; padding:18px 22px; border:1px solid #F0E6D8; box-shadow:0 4px 20px rgba(232,165,152,0.12); display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; margin-bottom:18px;">
  <div><div style="font-family:Caveat; font-size:28px; font-weight:700; color:#3A3A3A;">Bumil Planner 🤰</div><div style="font-size:11px; letter-spacing:2px; color:#9B8B7A; font-weight:600;">280 DAYS — DIY EDITION • V3 FIXED</div></div>
  <div><span style="background:#D9E4DD; border-radius:999px; padding:6px 14px; font-size:12px; border:1px solid #C8D9CF;">✨ Handmade with love</span> <span style="background:#FFF0EE; border-radius:999px; padding:6px 14px; font-size:12px; border:1px solid #F7D6D0;">💕 280 Hari</span></div>
</div>
""", unsafe_allow_html=True)

if st.session_state.use_gsheet:
    st.success("✅ Mode Cloud Aktif — Data di Google Sheets, bisa edit bareng")
else:
    st.warning("⚠️ Mode Lokal — Setting Google Sheets biar permanen")

tabs = st.tabs(["👤 Profil", "✅ To-Do Detail", "👶 Newborn", "💰 Budget", "💊 Vitamin & Makanan", "❓ Dokter + AI"])

with tabs[0]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### 👤 Profil")
    c1,c2 = st.columns(2)
    with c1:
        data["profil"]["nama_ibu"] = st.text_input("Nama Ibu", value=data["profil"]["nama_ibu"])
        data["profil"]["hpht"] = st.text_input("HPHT YYYY-MM-DD", value=data["profil"]["hpht"])
        if data["profil"]["hpht"]:
            try:
                hpht = datetime.strptime(data["profil"]["hpht"], "%Y-%m-%d")
                hpl = hpht + timedelta(days=280)
                st.info(f"HPL: {hpl.strftime('%d %B %Y')} — {(hpl - datetime.now()).days} hari lagi")
                data["profil"]["hpl"] = hpl.strftime("%Y-%m-%d")
            except: pass
        data["profil"]["bb_awal"] = st.text_input("BB awal kg", value=data["profil"]["bb_awal"])
        data["profil"]["tb"] = st.text_input("TB cm", value=data["profil"]["tb"])
    with c2:
        data["profil"]["rs_bidan"] = st.text_input("RS / Bidan", value=data["profil"]["rs_bidan"])
        data["profil"]["hp_dokter"] = st.text_input("HP Dokter", value=data["profil"]["hp_dokter"])
        data["profil"]["riwayat"] = st.text_area("Riwayat", value=data["profil"]["riwayat"])
    if st.button("💾 Simpan Profil"): save_all()
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown("#### ✅ To-Do List Super Lengkap - Per Bulan & Minggu")
    st.caption("✅ FIXED: Tidak ada tag HTML mentah lagi, keterangan tampil rapi")
    for bulan, tasks in data["todo"].items():
        selesai = len([t for t in tasks if t[2]])
        total = len(tasks)
        icon = "🌱" if "T1" in bulan else "🌸" if "T2" in bulan else "🌙"
        with st.expander(f"{icon} {bulan} — {selesai}/{total} selesai"):
            for idx, (nama, ket, done) in enumerate(tasks):
                c1,c2 = st.columns([0.06, 0.94])
                checked = c1.checkbox("", value=done, key=f"{bulan}_{idx}", label_visibility="collapsed")
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

with tabs[2]:
    st.markdown("#### 👶 Newborn List")
    cols = st.columns(3)
    for col_idx, kat in enumerate(["WAJIB PUNYA", "LUMAYAN PENTING", "TIDAK URGENT"]):
        with cols[col_idx]:
            st.markdown(f"**{kat}**")
            total = 0
            for i, item in enumerate(data["newborn"][kat]):
                with st.container(border=True):
                    item["done"] = st.checkbox(item["nama"], value=item["done"], key=f"{kat}_{i}_done")
                    item["qty"] = st.number_input("Qty", 1, 100, item["qty"], key=f"{kat}_{i}_qty")
                    item["harga"] = st.number_input("Harga Rp", 0, 10000000, item["harga"], key=f"{kat}_{i}_harga")
                    item["link"] = st.text_input("Link", value=item["link"], key=f"{kat}_{i}_link", placeholder="Shopee")
                    if item["link"]: st.link_button("Buka", item["link"])
                    if st.button("✕ Hapus", key=f"del_{kat}_{i}"):
                        data["newborn"][kat].pop(i); save_all(); st.rerun()
                    total += item["harga"]*item["qty"]
            st.metric(f"Total {kat}", f"Rp {total:,}")
    if st.button("💾 Simpan Newborn"): save_all()

with tabs[3]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### 💰 Budget")
    edited = st.data_editor(data["budget"], num_rows="dynamic", use_container_width=True, key="budget_fix")
    if st.button("Simpan Budget"):
        data["budget"] = edited; save_all()
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[4]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### 💊 Vitamin & Nutrisi Super Detail — Versi Lengkap Informatif")
    st.markdown('<div class="disclaimer-box">💡 Info umum, bukan resep pribadi. Konsul dokter untuk dosis personal.</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("##### 📋 Daftar Vitamin & Suplemen Wajib Per Trimester")
    v1,v2,v3 = st.columns(3)
    with v1:
        st.markdown("""
        <div class="vitamin-card" style="background:#F3F7F4;">
        <b>🌱 T1 (0-13 minggu) - Pembentukan Organ</b><br><br>
        <b>1. Asam Folat 400-800mcg</b><br>
        <small><b>Waktu:</b> Pagi setelah makan<br><b>Manfaat:</b> Cegah cacat tabung saraf (spina bifida), otak & sumsum tulang belakang<br><b>Makanan:</b> Bayam, brokoli, alpukat, kacang merah<br><b>Catatan:</b> WAJIB sejak program hamil. Riwayat cacat bisa naik ke 4mg resep dokter</small><br><br>
        <b>2. Vitamin D 600 IU</b><br>
        <small><b>Waktu:</b> Pagi bersama lemak<br><b>Manfaat:</b> Penyerapan kalsium, tulang, imun<br><b>Catatan:</b> Jika defisiensi bisa 1000-2000 IU</small><br><br>
        <b>3. Vitamin B6 10-25mg 3x/hari (jika mual berat)</b><br>
        <small><b>Manfaat:</b> Kurangi mual muntah<br><b>Catatan:</b> Harus resep dokter</small><br><br>
        <b>❌ HINDARI T1:</b><br>
        <small>- Vit A >10.000 IU<br>- Ibuprofen, retinol, jamu peluntur</small>
        </div>
        """, unsafe_allow_html=True)
    with v2:
        st.markdown("""
        <div class="vitamin-card" style="background:#FFF6F5;">
        <b>🌸 T2 (14-27 minggu) - Pertumbuhan Cepat</b><br><br>
        <b>2. Kalsium 1000mg/hari</b><br>
        <small><b>Waktu:</b> Malam, JAUH dari Fe (jeda 2-3 jam)<br><b>Manfaat:</b> Gigi & tulang bayi, cegah kram & preeklamsia<br><b>Makanan:</b> Susu hamil 2 gelas, yogurt, keju cheddar pasteurisasi, teri<br><b>Tanda kurang:</b> Gigi ngilu, kram malam</small><br><br>
        <b>3. Zat Besi 27mg/hari</b><br>
        <small><b>Waktu:</b> Malam + Vit C (jeruk)<br><b>Manfaat:</b> Cegah anemia, oksigen ke janin<br><b>Jangan bareng:</b> Susu, kopi, teh<br><b>Efek:</b> BAB hitam wajar</small><br><br>
        <b>4. DHA 200-300mg/hari</b><br>
        <small><b>Waktu:</b> Siang setelah makan berlemak<br><b>Manfaat:</b> Otak, mata, saraf janin<br><b>Makanan:</b> Salmon, lele, kembung rendah merkuri</small><br><br>
        <b>5. Magnesium 300mg (jika kram)</b><br>
        <small><b>Waktu:</b> Malam<br><b>Manfaat:</b> Relaksasi otot, tidur</small>
        </div>
        """, unsafe_allow_html=True)
    with v3:
        st.markdown("""
        <div class="vitamin-card" style="background:#FFFCF8;">
        <b>🌙 T3 (28-40 minggu) - Persiapan Lahiran</b><br><br>
        <b>1. Lanjut Fe + Ca + DHA + Vit D</b><br>
        <small>Kebutuhan puncak, Hb target >11. Jika <10, dokter naikkan Fe 60mg</small><br><br>
        <b>2. Vitamin K (36+ minggu jika saran dokter)</b><br>
        <small><b>Manfaat:</b> Pembekuan darah, cegah perdarahan lahir<br><b>Makanan:</b> Bayam, brokoli, alpukat</small><br><br>
        <b>3. Magnesium Lanjut</b><br>
        <small><b>Manfaat:</b> Kurangi kontraksi palsu, kram, bantu tidur</small><br><br>
        <b>4. Probiotik & Laktasi</b><br>
        <small>Yogurt plain, tempe, untuk pencernaan & persiapan ASI. Mulai pijat payudara lembut</small><br><br>
        <b>Catatan:</b><br>
        <small>- Jangan jamu pelancar tanpa dokter<br>- Minum Fe sampai 3 bulan nifas</small>
        </div>
        """, unsafe_allow_html=True)
    st.divider()
    st.markdown("##### 🥗 Makanan WAJIB - Detail")
    w1,w2 = st.columns(2)
    with w1:
        st.markdown("""
        **1. Protein 60-80gr/hari**
        - Kenapa: Otot, otak, plasenta, air ketuban
        - Porsi: 3-4 porsi (1 telur + 50gr ayam/ikan + 100gr tempe)
        - Menu: Pagi telur 2 + susu, Siang ayam 100gr + tempe 100gr, Malam ikan lele/salmon 100gr + tahu
        - Tips: Variasikan hewani + nabati

        **2. Zat Besi + Folat + Vit C**
        - Kenapa: Cegah anemia, BBLR
        - Fe heme: Daging sapi 1-2x/mgg, hati ayam 1x/mgg MAX 50gr
        - Non-heme: Bayam, kacang merah, alpukat, brokoli
        - Wajib + Vit C: Jeruk, jambu, kiwi biar serap 2-3x
        - Jangan bareng susu/kopi/teh/kalsium

        **3. Kalsium 1000mg/hari**
        - Porsi: 3-4 porsi (1 gelas susu 250ml = 300mg)
        - Menu: Pagi susu hamil 250ml, Snack yogurt 100gr, Malam keju cheddar / teri 50gr
        - Jika intoleransi: Susu kedelai kalsium tinggi + tahu + brokoli
        """)
    with w2:
        st.markdown("""
        **4. Serat 25-30gr + Air 2.3-2.5L**
        - Kenapa: Progesteron bikin sembelit, Fe bikin sembelit
        - Sumber: Pepaya MATANG 100gr, pisang, apel, oat 30gr, sayur 5 porsi warna-warni
        - Air: 8-10 gelas, bawa botol

        **5. Lemak Sehat DHA & Kolin**
        - Kenapa: 70% otak janin lemak
        - Sumber: Salmon, lele, kembung 2x/mgg, telur omega-3 1/hari, alpukat 1/2, almond 10 butir
        - Kolin: Kuning telur, kedelai

        **6. Karbo Kompleks & Probiotik**
        - Karbo: Nasi merah, kentang, ubi, oat — butuh energi lahiran
        - Probiotik: Yogurt plain, tempe, kimchi halal — pencernaan & imun
        """)
    st.divider()
    st.markdown("##### ⛔ Makanan HINDARI / BATASI - Risiko & Alternatif Aman")
    h1,h2 = st.columns(2)
    with h1:
        st.markdown("""
        **1. Sushi mentah, sashimi, kerang mentah**
        - Risiko: Anisakis, Listeria → keguguran, prematur
        - Alternatif: Sushi matang tempura, salmon panggang >63°C

        **2. Daging, ayam, telur setengah matang, sate mentah**
        - Risiko: Toksoplasma, Salmonella → cacat, diare berat
        - Aman: Tidak ada pink, suhu >75°C, telur tidak cair

        **3. Susu mentah & keju lunak tidak pasteurisasi (brie, feta, camembert)**
        - Risiko: Listeria → infeksi janin
        - Cek: Harus ada pasteurized / UHT
        - Aman: Susu UHT, yogurt pasteurisasi, cheddar

        **4. Ikan merkuri tinggi: Hiu, Todak, King Mackerel, Tuna Bigeye**
        - Risiko: Merkuri rusak saraf & otak janin
        - Aman rendah merkuri: Lele, salmon, kembung, nila, udang (200-300gr/mgg)
        """)
    with h2:
        st.markdown("""
        **5. Kafein >200mg (~1 kopi kecil) & Energi drink**
        - Risiko: BBLR, keguguran jika berlebihan
        - Hitungan: Kopi 95mg, teh 47mg
        - Aman: Max 1 gelas kecil/hari, ganti decaf / susu

        **6. Alkohol 0 & Rokok / Vape 0**
        - Risiko: Fetal Alcohol Syndrome, BBLR, plasenta lepas
        - Termasuk jamu beralkohol, vape, rokok pasif

        **7. Jamu gendong tidak jelas, nanas muda & pepaya muda berlebihan**
        - Risiko: Kontraksi dini, ketuban pecah dini
        - Nanas matang 1-2 potong aman, muda yang bahaya
        - Pepaya muda ada papain, matang aman atasi sembelit

        **8. Ultra-processed tinggi garam, gula, soda**
        - Risiko: Hipertensi, preeklamsia, diabetes gestasional
        - Ganti: Buah, kacang sangrai tanpa garam, air putih
        """)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[5]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### ❓ Dokter + AI - FAQ Lengkap Per Trimester (Versi Super Lengkap)")
    st.markdown('<div class="disclaimer-box">⚠️ <b>DISCLAIMER:</b> Semua jawaban info UMUM & EDUKASI, bukan diagnosis pribadi. Untuk kepastian, WAJIB konsultasi dokter/bidan. Tanda bahaya (perdarahan banyak, ketuban pecah, gerakan &lt;10x/12jam, demam &gt;38.5, nyeri hebat) segera IGD.</div>', unsafe_allow_html=True)
    sub1, sub2 = st.tabs(["📝 Tracker", "💬 FAQ Lengkap + AI Dokter"])
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
        st.markdown("##### ❓ FAQ Umum — Selalu Ditanya (8 FAQ)")
        faqs_umum = [
            ("Apakah hasil lab saya normal?", "Hb normal >11 g/dL. Jika <11 anemia, tambah Fe. Gula puasa <92. Protein urine negatif normal, +1/+2 waspada preeklamsia. Gol darah penting antisipasi perdarahan."),
            ("Apakah BB saya naik sesuai?", "T1 naik 1-2kg total wajar. T2-T3 0.35-0.5kg/minggu. Total tergantung BMI: Kurus 12.5-18kg, Normal 11.5-16kg, Gemuk 7-11.5kg, Obesitas 5-9kg. Naik >1kg/minggu + bengkak + tensi naik = kontrol."),
            ("Vitamin apa yang perlu lanjut?", "T1: Folat+Vit D. T2: +Ca malam, Fe malam+Vit C, DHA siang. T3: Lanjut semua + Mg jika kram. Jangan stop tanpa dokter."),
            ("Boleh HB?", "Boleh jika tidak flek, ketuban tidak rembes, tidak plasenta previa, dokter tidak larang. Posisi woman on top, side lying nyaman."),
            ("Boleh naik pesawat?", "Aman sampai 28 minggu bebas, 28-36 butuh surat dokter, >36 ditolak maskapai. Hindari >4 jam, jalan tiap 1-2 jam."),
            ("Kapan kontrol berikutnya?", "T1 4 mingguan, T2 4 mingguan + USG anomali 20-22 minggu, T3 awal 2 mingguan + CTG, T3 akhir mingguan."),
            ("Apa yang harus diwaspadai?", "Perdarahan banyak, ketuban pecah banyak tidak bisa ditahan, gerakan <10x/12 jam, demam >38.5, muntah terus >24 jam, nyeri hebat, pusing + pandangan kabur + nyeri ulu hati."),
            ("Boleh cat rambut, skincare?", "T1 hindari dulu. T2-T3 boleh cat tanpa amonia ventilasi baik. Hindari retinol, hydroquinone, formalin."),
        ]
        for q,a in faqs_umum:
            with st.expander(q): st.write(a)
        st.markdown("##### 🌱 FAQ Trimester 1 (10 FAQ)")
        faqs_t1 = [
            ("Apakah mual berat normal?", "Normal karena hCG. Makan kecil 5-6x, biskuit sebelum bangun. Jika tidak bisa makan/minum >24 jam, muntah >5x/hari, BB turun >5%, pipis sedikit gelap, pusing pingsan → hiperemesis, segera kontrol."),
            ("Flek kecoklatan bahaya?", "Bisa implantasi minggu 4-6, sedikit 1-2 hari. Bedakan ancaman keguguran. Kontrol jika darah merah segar banyak, kram hebat, ada jaringan. Istirahat total, jangan HB."),
            ("Kapan DJJ terdengar?", "USG transvaginal 6-7 minggu kedip, perut 8-10 minggu, doppler 10-12 minggu. Jika 8 minggu belum ada, cek ulang 1-2 minggu lagi."),
            ("Kenapa sering pipis & sembelit?", "Rahim tekan kandung kemih + progesteron lambatkan usus. Jangan tahan pipis, minum 2.3L tapi kurangi sebelum tidur, serat 25gr."),
            ("Mood swing nangis terus?", "Hormon naik turun + cemas. Curhat suami, tidur cukup, jalan pagi, komunitas bumil. Jika sedih >2 minggu, tidak nafsu makan, tidak bisa tidur, konsul dokter."),
            ("Boleh olahraga T1?", "Boleh ringan: jalan 20 menit, yoga T1, stretching. Hindari lari, lompat, angkat >5kg, kontak. Stop jika flek."),
            ("Makanan paling penting T1?", "Fokus folat & protein: bayam, brokoli, alpukat, telur matang, ayam, lele. Hindari sushi mentah, setengah matang, alkohol."),
            ("Kapan USG pertama ideal?", "6-8 minggu konfirmasi dalam rahim & DJJ, 11-13 minggu USG NT screening down syndrome."),
            ("Boleh kerja berat & naik motor?", "Hindari angkat >10kg, berdiri >4 jam, motor jauh jalan rusak. Jarak dekat pelan boleh."),
            ("Keputihan awal hamil?", "Putih susu tidak gatal tidak bau wajar. Jika kuning/hijau, gatal hebat, bau amis, perih pipis → infeksi, kontrol."),
        ]
        for q,a in faqs_t1:
            with st.expander(q): st.write(a)
        st.markdown("##### 🌸 FAQ Trimester 2 (10 FAQ)")
        faqs_t2 = [
            ("Kapan gerakan janin pertama?", "Anak pertama 18-22 minggu, anak kedua 16 minggu. Awal seperti kupu-kupu. Jika 22 minggu belum sama sekali, kontrol."),
            ("Sakit punggung, kram kaki?", "Rahim membesar ubah tumpu + butuh kalsium. Pakai bantal hamil, sepatu flat, kalsium 1000mg malam, magnesium, pijat punggung."),
            ("Posisi tidur terbaik?", "Miring kiri terbaik aliran darah. Pakai 2-3 bantal: bawah perut, antara kaki, belakang punggung. Hindari telentang lama."),
            ("Perut kencang Braxton Hicks?", "Normal T2 akhir, tidak teratur, hilang istirahat/minum. Tidak normal jika teratur 10 menit sekali, makin kuat, ada flek/lendir darah → kontraksi prematur ke RS."),
            ("Boleh pijat hamil?", "Boleh >14 minggu terapis khusus bumil, posisi miring/duduk, hindari perut & titik tumit dalam, minyak keras. Hindari jika flek, ketuban rembes, preeklamsia."),
            ("Boleh puasa?", "Konsul dokter. Jika sehat, BB janin normal, tidak diabetes/anemia berat, boleh dengan sahur buka lengkap, minum 2.5L, istirahat. Batal jika pusing berat, gerakan berkurang."),
            ("Ngidam aneh?", "Ngidam makanan wajar. Jika ngidam bukan makanan (tanah, kapur, es batu banyak) → pica tanda anemia, cek Hb."),
            ("BB naik ideal T2?", "0.35-0.5kg/minggu. Jika >1kg/minggu mendadak + bengkak wajah/tangan + tensi naik waspada preeklamsia."),
            ("Boleh travelling mobil?", "Boleh <6 jam, tiap 1-2 jam berhenti jalan 5-10 menit, seatbelt bawah perut, bawa KIA."),
            ("Gusi berdarah & mimisan?", "Hormon bikin gusi bengkak & pembuluh hidung rapuh. Sikat bulu lembut, kumur garam, vit C. Jika mimisan >20 menit tidak berhenti ke dokter."),
        ]
        for q,a in faqs_t2:
            with st.expander(q): st.write(a)
        st.markdown("##### 🌙 FAQ Trimester 3 (12 FAQ Super Lengkap)")
        faqs_t3 = [
            ("Bedanya kontraksi palsu vs asli?", "PALSU: Tidak teratur, jarak jauh tidak makin dekat, pendek, hilang istirahat/minum, hanya depan. ASLI: Teratur 10->5->3 menit, durasi 40-60 detik, makin kuat tidak hilang, ada lendir darah."),
            ("Kapan harus ke RS?", "Rumus 5-1-1: Kontraksi tiap 5 menit durasi 1 menit selama 1 jam. ATAU ketuban pecah banyak tidak bisa ditahan, ATAU perdarahan banyak, ATAU gerakan <10x/12 jam, ATAU pusing berat + pandangan kabur + nyeri ulu hati."),
            ("Ketuban pecah warna hijau/kuning/bau?", "Segera RS. Hijau/kuning janin BAB di dalam (stress), bau infeksi. Jangan masukin apa pun ke vagina, jangan HB, jangan berendam, catat jam pecah."),
            ("Sungsang / melintang bisa muter?", "Bisa sampai 34-36 minggu. Knee-chest 15 menit 2x/hari (jika tidak kontraindikasi), moxibustion, berenang, yoga. Di atas 36 minggu menetap diskusi ECV atau SC."),
            ("Bolehkah induksi alami?", "Jalan, squat, birth ball, stimulasi puting lembut, HB (sperma prostaglandin) bisa jika >37 minggu & tidak kontraindikasi. Nanas muda & jamu pelancar JANGAN tanpa dokter."),
            ("Apa itu CTG & doppler?", "CTG rekam DJJ & kontraksi, lihat janin stress. Doppler cek aliran tali pusat & plasenta. Dilakukan T3 jika gerakan berkurang, hipertensi, diabetes, lewat HPL."),
            ("Perineal massage perlu?", "Sangat disarankan 34 minggu, tiap malam 5-10 menit VCO, pijat perineum biar elastis, kurangi robekan derajat 3-4."),
            ("ASI belum keluar di hamil, normal?", "Normal, ASI matang baru keluar setelah plasenta lahir hari 2-3. Yang keluar kolostrum sedikit kuning wajar. Jangan dipencet kuat."),
            ("Bengkak kaki & tangan kapan bahaya?", "Bengkak sore normal. Bahaya jika mendadak wajah/tangan + tensi >140/90 + protein urine + pusing/nyeri ulu hati → preeklamsia IGD."),
            ("Baby blues & mental?", "Wajar cemas takut tidak bisa jadi ibu baik. Belajar mandikan, gendong, sendawakan, ikut kelas ayah siaga, support system, tidur saat bayi tidur. Jika sedih >2 minggu tidak mau makan tidak sayang bayi, konsul psikolog."),
            ("Isi tas RS wajib?", "Ibu: KTP KK BPJS buku nikah KIA, baju kancing depan 3, pembalut nifas, underwear, bra, sandal, charger, camilan. Bayi: Baju 5, bedong 3, popok NB, topi, kaos kaki, tisu basah, selimut. Ayah: KTP, uang cash, baju ganti."),
            ("Lewat HPL belum lahiran?", "HPL perkiraan, normal 37-42 minggu. 40 minggu belum tanda cek CTG + USG ketuban. 41 minggu diskusi induksi. 42 minggu biasanya induksi karena plasenta menua."),
        ]
        for q,a in faqs_t3:
            with st.expander(q): st.write(a)
        st.divider()
        st.markdown("### 👩‍⚕️ Tanya AI Dokter OBGYN (Jawaban Umum)")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [{"role": "ai", "content": "Halo Bunda! 👋 Saya AI edukasi OBGYN. Tanya apa saja umum (mual, flek, kram, vitamin, makanan, tanda lahiran). Jawaban saya info umum ya."}]
        kb = {"mual": "Mual T1 normal karena hCG. Tips: porsi kecil 5-6x, biskuit bangun tidur, jahe hangat. Jika >24 jam tidak makan/minum, kontrol.", "flek": "Flek sedikit bisa implantasi, tapi tetap kontrol. Istirahat, hindari HB. Segera RS jika darah merah segar banyak, kram hebat.", "makanan": "Wajib protein 60-80gr, Fe+Vit C, Ca 1000mg, serat, air 2.3L. Hindari sushi mentah, daging setengah matang, susu mentah, ikan merkuri tinggi, kafein >200mg, alkohol 0.", "lahiran": "Tanda asli: 5-1-1, lendir darah, ketuban pecah banyak. Segera RS jika 5-1-1, ketuban pecah, perdarahan, gerakan <10x/12jam.", "gerakan": "Mulai 18-22 minggu halus. T3 hitung 10 gerakan/12 jam. Jika <10, segera RS."}
        def get_answer(q):
            ql=q.lower()
            for k,v in kb.items():
                if k in ql: return v+"\n\nIni info umum ya, untuk kepastian konsultasi dokter ya."
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

st.markdown('<div style="text-align:center; font-family:Caveat; font-size:18px; color:#9B8B7A; margin-top:30px;">"Setiap tendangan kecil adalah cerita besar" 🌸</div>', unsafe_allow_html=True)
