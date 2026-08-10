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
            "T1 - Bulan 1 (Minggu 1-4)": [
                ("Tes pack & catat HPHT", "Pagi hari, urine pertama untuk hasil akurat", False),
                ("Hitung HPL HPHT+280", "Gunakan kalkulator online atau kalender", False),
                ("Mulai asam folat 400-800mcg", "Penting mencegah cacat tabung saraf, setelah makan", False),
                ("Stop rokok/alkohol/vape", "0 toleransi untuk kesehatan janin", False),
                ("Cek obat aman bumil?", "Tanya dokter sebelum minum obat bebas", False),
                ("Daftar dokter/bidan & buku KIA", "Pilih faskes terdekat yang nyaman", False),
                ("Buat folder dokumen KK KTP BPJS", "Fotokopi 3x untuk persiapan admin RS", False),
                ("Cek BPJS/asuransi", "Pastikan aktif dan pelajari coveragenya", False),
                ("Tidur 7-8 jam", "Miring kiri lebih baik untuk aliran darah", False),
                ("Air 2.3L/hari", "Bawa botol minum ke mana-mana", False),
                ("Kurangi kafein", "Maksimal 1 gelas kopi/teh sehari", False),
                ("Hindari daging/ikan mentah", "Risiko listeria dan bakteri berbahaya", False),
                ("Prenatal vitamin tambahan", "Konsul dokter untuk vitamin D dan lainnya", False)
            ],
            "T1 - Bulan 2 (Minggu 5-8)": [
                ("USG pertama kantung & DJJ", "6-8 minggu, pastikan janin di dalam rahim", False),
                ("Lab darah lengkap", "Hb, HIV, HepB, Sifilis, Golongan Darah", False),
                ("Cek TSH tiroid", "Penting untuk perkembangan otak janin awal", False),
                ("Atasi mual porsi kecil", "Makan 5-6x porsi kecil, biskuit bangun tidur", False),
                ("Beli bra hamil", "Tanpa kawat, bahan katun menyerap keringat", False),
                ("Catat BB mingguan", "Setiap Senin pagi saat perut kosong", False),
                ("Hindari sushi mentah", "Hanya makan yang matang sempurna", False),
                ("Prenatal yoga 15 menit", "Stretching ringan di rumah", False),
                ("Istirahat cukup siang hari", "Tidur siang 30-45 menit jika lelah", False),
                ("Cek produk skincare", "Hindari retinol, BHA, dan paraben", False),
                ("Minum jahe hangat", "Untuk meredakan mual dan kembung", False),
                ("Jaga kebersihan gigi", "Sikat 2x sehari, hindari gusi berdarah", False),
                ("Hindari angkat beban berat", "Minta bantuan untuk barang >5kg", False)
            ],
            "T1 - Bulan 3 (Minggu 9-13)": [
                ("USG NT 11-13 / NIPT", "Skrining kelainan kromosom, opsional tapi penting", False),
                ("Konsultasi hasil lab", "Bawa semua hasil ke obgyn di kunjungan berikutnya", False),
                ("Atur cuti hamil", "Pelajari hak cuti di kantor dari sekarang", False),
                ("Minyak anti stretch mark", "Oleskan di perut, paha, dan payudara 2x sehari", False),
                ("List pertanyaan dokter T1", "Siapkan catatan di HP agar tidak lupa", False),
                ("Financial plan awal", "Buat tabungan khusus biaya lahiran", False),
                ("Beli bantal hamil", "Bentuk U atau C untuk kenyamanan tidur", False),
                ("Hindari aktivitas ekstrem", "Stop olahraga high-impact sementara", False),
                ("Pilih baju hamil longgar", "Cari celana dengan karet perut khusus", False),
                ("Sering cuci tangan", "Cegah infeksi virus seperti CMV/Tokso", False),
                ("Konsumsi kalsium alami", "Susu pasteurisasi, keju matang, yoghurt", False),
                ("Cek berat badan", "Pastikan kenaikan T1 tidak terlalu drastis", False),
                ("Umumkan kehamilan", "Opsional, setelah lewat trimester pertama yang rawan", False)
            ],
            "T2 - Bulan 4 (Minggu 14-17)": [
                ("USG anatomi awal", "Cek struktur janin secara umum", False),
                ("Kalsium 1000mg & zat besi 27mg", "Jika saran dokter, pisahkan minumnya 2 jam", False),
                ("Kelas hamil online", "Ikuti webinar edukasi kehamilan", False),
                ("Skincare bumil-friendly", "Pastikan produk yang dipakai aman no retinol", False),
                ("Tidur miring kiri", "Gunakan bantal penyangga di antara kaki", False),
                ("Baju hamil 2-3 stel", "Siapkan untuk perut yang mulai membesar", False),
                ("Jalan 20-30 menit", "Jalan santai pagi atau sore hari", False),
                ("Ngobrol dengan janin", "Ajak bicara, pendengaran janin mulai berkembang", False),
                ("Makan serat 25-30gr", "Sayur hijau, buah pepaya matang untuk cegah sembelit", False),
                ("Hindari tidur telentang lama", "Agar aliran darah ke rahim tidak terhambat", False),
                ("Perawatan gigi", "Ke dokter gigi untuk pembersihan karang gigi", False),
                ("Cek asuransi newborn", "Persiapkan asuransi tambahan untuk bayi jika ada", False),
                ("Senam kegel dasar", "Mulai latih otot dasar panggul 3x10 repetisi", False)
            ],
            "T2 - Bulan 5 (Minggu 18-22)": [
                ("USG anomali detail 20 minggu WAJIB", "Screening kelainan organ bawaan 20-22 minggu", False),
                ("Cek Hb & gula puasa", "Skrining anemia T2 dan kesiapan tubuh", False),
                ("Catat gerakan janin", "Quickening, rasakan tendangan halus pertama", False),
                ("Riset pompa ASI & bouncer", "Bandingkan merk dan harga di e-commerce", False),
                ("Brainstorm 10 nama bayi", "Buat daftar nama laki-laki dan perempuan", False),
                ("Moodboard kamar bayi", "Cari inspirasi dekorasi di Pinterest", False),
                ("Planning foto maternity", "Booking fotografer jika berencana foto", False),
                ("Konsumsi DHA 200-300mg", "Penting untuk perkembangan otak janin", False),
                ("Mulai pijat kehamilan", "Boleh dilakukan >14 minggu oleh terapis khusus", False),
                ("Cek keputihan", "Bila bau/gatal segera lapor dokter", False),
                ("Latihan relaksasi", "Meditasi 10 menit untuk tenangkan pikiran", False),
                ("Hindari berdiri terlalu lama", "Cegah varises dan kaki bengkak", False),
                ("Periksa tekanan darah", "Waspada hipertensi kehamilan / preeklamsia ringan", False)
            ],
            "T2 - Bulan 6 (Minggu 23-27)": [
                ("TTGO 24-28 minggu", "Tes toleransi glukosa untuk cek diabetes gestasional", False),
                ("Vaksin Tdap & flu", "Konsul dokter, penting untuk antibodi janin", False),
                ("Cek plasenta", "USG pastikan tidak menutupi jalan lahir / plasenta previa", False),
                ("Senam kegel 3x10", "Rutin tiap hari untuk perkuat otot panggul", False),
                ("Edukasi ASI", "Nonton video pelekatan dan posisi menyusui yang benar", False),
                ("Draft birth plan", "Tulis harapan proses persalinan untuk didiskusikan", False),
                ("Cicil perlengkapan WAJIB 50%", "Beli baju newborn, popok, alat mandi", False),
                ("Latihan senam hamil", "Ikuti kelas atau video panduan senam hamil", False),
                ("Kurangi garam", "Cegah kaki bengkak yang berlebihan", False),
                ("Stretching punggung bawah", "Lakukan cat-cow pose perlahan", False),
                ("Cek persiapan finansial", "Evaluasi tabungan lahiran di pertengahan T2", False),
                ("Ikut komunitas ibu hamil", "Gabung grup WA/FB untuk sharing", False),
                ("Sering angkat kaki", "Tinggikan kaki saat duduk istirahat 15 menit", False)
            ],
            "T3 - Bulan 7 (Minggu 28-31)": [
                ("USG pertumbuhan & doppler", "Cek berat janin dan aliran darah plasenta", False),
                ("Cek posisi kepala", "Pastikan kepala mulai di bawah / tidak sungsang", False),
                ("Packing tas RS 70%", "Siapkan tas, cicil masukin barang perlengkapan ibu", False),
                ("Kelas napas & hypnobirthing", "Belajar teknik napas kurangi sakit kontraksi", False),
                ("Berkas KTP KK buku nikah BPJS", "Jadikan 1 map khusus, fotokopi masing-masing 5x", False),
                ("Beli gendongan SSC", "Pilih yang ergonomic M-shape support", False),
                ("Finalisasi cuti", "Serahkan form cuti hamil ke HRD kantor", False),
                ("Lanjut kalsium & zat besi", "Sangat penting di trimester 3 untuk tulang janin", False),
                ("Cek kontraksi palsu", "Braxton Hicks, bedakan dengan kontraksi asli", False),
                ("Cuci pakaian bayi", "Gunakan deterjen khusus bayi, tanpa pewangi keras", False),
                ("Susun rak/lemari bayi", "Rapikan baju dan popok bayi di kamar", False),
                ("Latihan panggul", "Gunakan birthing ball untuk goyang panggul ringan", False),
                ("Kenali tanda persalinan", "Pahami beda air ketuban, keputihan, dan urine", False)
            ],
            "T3 - Bulan 8 (Minggu 32-36)": [
                ("Kontrol 2 mingguan", "Jadwal ke obgyn jadi lebih sering", False),
                ("CTG & cek preeklamsia", "Cek detak jantung janin dan tensi/protein urine", False),
                ("Finalisasi kamar bayi", "Pastikan sirkulasi udara baik, pasang kelambu", False),
                ("Belajar mandikan bedong gendong", "Latihan pakai boneka bersama suami", False),
                ("Sterilisasi botol", "Cuci bersih dan sterilkan alat pompa & botol", False),
                ("Kontak darurat RS bidan driver", "Tempel di kulkas agar mudah dilihat", False),
                ("Pengaman rumah", "Cek keamanan lingkungan, nomor satpam", False),
                ("Perineal massage", "Mulai pijat area perineum dengan minyak VCO", False),
                ("Hitung gerakan janin", "Pastikan minimal 10 gerakan dalam 12 jam", False),
                ("Kurangi perjalanan jauh", "Hindari keluar kota jika tidak mendesak", False),
                ("Posisi sujud", "Knee-chest pose 15 menit untuk bantu bayi masuk panggul", False),
                ("Diskusi SC vs Normal", "Bicarakan opsi persalinan dengan dokter", False),
                ("Afirmasi positif harian", "Dengarkan audio hypnobirthing tiap malam", False)
            ],
            "T3 - Bulan 9 (Minggu 37-40)": [
                ("Kontrol mingguan", "Wajib cek ke dokter setiap minggu di bulan 9", False),
                ("Cek panggul", "Pemeriksaan dalam jika diperlukan oleh dokter", False),
                ("Packing tas RS 100%", "Baju ibu 3 set, baju bayi 5 set, dokumen lengkap, masukkan ke mobil", False),
                ("Latihan napas 4-7-8", "Praktikkan teknik napas saat perut kencang", False),
                ("Siaga tanda persalinan 5-1-1", "Kontraksi tiap 5 menit, durasi 1 menit, selama 1 jam", False),
                ("Rute tercepat RS", "Survei jalan alternatif saat macet ke RS", False),
                ("Stok frozen food", "Siapkan makanan mudah panaskan untuk minggu awal postpartum", False),
                ("Cek ketuban rembes", "Pakai pantyliner untuk cek jika ada cairan jernih keluar", False),
                ("Rileks & jalan pagi", "Jalan kaki 30 menit setiap hari bantu bayi turun", False),
                ("Hubungan suami istri", "Boleh jika dokter setuju, prostaglandin bantu lunakkan serviks", False),
                ("Pijat oksitosin", "Minta suami pijat punggung stimulasi hormon persalinan", False),
                ("Cukur area intim", "Opsional, rapikan bulu kemaluan untuk kebersihan", False),
                ("Lepas cincin perhiasan", "Simpan perhiasan di rumah, antisipasi bengkak", False)
            ],
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

    total_all = sum(len(tasks) for tasks in data["todo"].values())
    selesai_all = sum(len([t for t in tasks if t[2]]) for tasks in data["todo"].values())

    st.progress(selesai_all / total_all if total_all > 0 else 0)
    st.markdown(f"**Progress Keseluruhan:** {selesai_all} / {total_all} tugas selesai")

    with st.expander("🔄 Reset To-Do ke Versi Super Detail Terbaru"):
        if st.button("Reset To-Do"):
            data["todo"] = default_data()["todo"]
            save_all()
            st.rerun()

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
                    st.markdown(f"<span style='font-size:12px; color:#9B8B7A;'>{ket}</span>", unsafe_allow_html=True)
                if checked != done:
                    data["todo"][bulan][idx] = (nama, ket, checked)
                    save_all()
                    st.rerun()
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
    st.markdown("#### 💊 Vitamin & Nutrisi Super Detail — Versi Lengkap Informatif")
    st.markdown('<div class="disclaimer-box">💡 <b>Info umum edukasi, bukan resep pribadi.</b> Dosis personal tetap konsul dokter. Hindari Vitamin A >10.000 IU, ibuprofen tanpa resep, dan jamu tidak jelas.</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("##### 📋 Daftar Vitamin & Suplemen Wajib Per Trimester")
    v1,v2,v3 = st.columns(3)
    with v1:
        st.markdown("""
        <div style="background:#F3F7F4; border-radius:18px; padding:16px; border:1px solid #D9E4DD;">
        <b>🌱 T1 (0-13 minggu) - Pembentukan Organ</b><br><br>
        <b>1. Asam Folat 400-800mcg</b><br>
        <small><b>Waktu:</b> Pagi setelah makan<br><b>Manfaat:</b> Cegah cacat tabung saraf (spina bifida)<br><b>Makanan:</b> Bayam, brokoli, alpukat, kacang merah<br><b>Catatan:</b> WAJIB sejak program hamil</small><br><br>
        <b>2. Vitamin D 600 IU</b><br>
        <small><b>Waktu:</b> Pagi bersama lemak<br><b>Manfaat:</b> Penyerapan kalsium, tulang, imun</small><br><br>
        <b>3. Vitamin B6 10-25mg 3x/hari (jika mual berat)</b><br>
        <small><b>Manfaat:</b> Kurangi mual muntah</small><br><br>
        <b>❌ HINDARI T1:</b> Vit A >10.000 IU, Ibuprofen, retinol, jamu peluntur
        </div>
        """, unsafe_allow_html=True)
    with v2:
        st.markdown("""
        <div style="background:#FFF6F5; border-radius:18px; padding:16px; border:1px solid #F7D6D0;">
        <b>🌸 T2 (14-27 minggu) - Pertumbuhan Cepat</b><br><br>
        <b>2. Kalsium 1000mg/hari</b><br>
        <small><b>Waktu:</b> Malam, JAUH dari Fe 2-3 jam<br><b>Manfaat:</b> Gigi & tulang bayi, cegah kram & preeklamsia<br><b>Makanan:</b> Susu hamil 2 gelas, yogurt, cheddar pasteurisasi</small><br><br>
        <b>3. Zat Besi 27mg/hari</b><br>
        <small><b>Waktu:</b> Malam + Vit C (jeruk)<br><b>Manfaat:</b> Cegah anemia<br><b>Jangan bareng:</b> Susu, kopi, teh</small><br><br>
        <b>4. DHA 200-300mg/hari</b><br>
        <small><b>Waktu:</b> Siang setelah makan<br><b>Manfaat:</b> Otak, mata, saraf janin<br><b>Makanan:</b> Salmon, lele, kembung rendah merkuri</small><br><br>
        <b>5. Magnesium 300mg (jika kram)</b><br>
        <small>Malam, relaksasi otot, bantu tidur</small>
        </div>
        """, unsafe_allow_html=True)
    with v3:
        st.markdown("""
        <div style="background:#FFFCF8; border-radius:18px; padding:16px; border:1px solid #F0E6D8;">
        <b>🌙 T3 (28-40 minggu) - Persiapan Lahiran</b><br><br>
        <b>1. Lanjut Fe + Ca + DHA + Vit D</b><br>
        <small>Kebutuhan puncak, Hb target >11</small><br><br>
        <b>2. Vitamin K (36+ minggu jika saran dokter)</b><br>
        <small><b>Manfaat:</b> Pembekuan darah, cegah perdarahan lahir<br><b>Makanan:</b> Bayam, brokoli, alpukat</small><br><br>
        <b>3. Magnesium Lanjut</b><br>
        <small>Kurangi kontraksi palsu, kram, bantu tidur</small><br><br>
        <b>4. Probiotik & Laktasi</b><br>
        <small>Yogurt plain, tempe, untuk pencernaan & persiapan ASI</small><br><br>
        <b>Catatan:</b> Minum Fe sampai 3 bulan nifas
        </div>
        """, unsafe_allow_html=True)
    st.divider()
    st.markdown("##### 🥗 Makanan WAJIB - Detail")
    w1,w2 = st.columns(2)
    with w1:
        st.markdown("""
        **1. Protein 60-80gr/hari**\n- Kenapa: Otot, otak, plasenta, air ketuban\n- Porsi: 3-4 porsi (1 telur + 50gr ayam/ikan + 100gr tempe)\n- Menu: Pagi telur 2 + susu, Siang ayam 100gr + tempe 100gr, Malam ikan lele/salmon 100gr + tahu\n\n**2. Zat Besi + Folat + Vit C**\n- Fe heme: Daging sapi 1-2x/mgg, hati ayam 1x/mgg MAX 50gr\n- Non-heme: Bayam, kacang merah, alpukat, brokoli\n- Wajib + Vit C: Jeruk, jambu, kiwi biar serap 2-3x\n- Jangan bareng susu/kopi/teh/kalsium\n\n**3. Kalsium 1000mg/hari**\n- Porsi: 3-4 porsi (1 gelas susu 250ml = 300mg)\n- Menu: Pagi susu hamil 250ml, Snack yogurt 100gr, Malam cheddar / teri 50gr
        """)
    with w2:
        st.markdown("""
        **4. Serat 25-30gr + Air 2.3-2.5L**\n- Sumber: Pepaya MATANG 100gr, pisang, apel, oat 30gr, sayur 5 porsi\n- Air: 8-10 gelas, bawa botol\n\n**5. Lemak Sehat DHA & Kolin**\n- Sumber: Salmon, lele, kembung 2x/mgg, telur omega-3 1/hari, alpukat 1/2, almond 10 butir\n- Kolin: Kuning telur, kedelai\n\n**6. Karbo Kompleks & Probiotik**\n- Karbo: Nasi merah, kentang, ubi, oat — butuh energi lahiran\n- Probiotik: Yogurt plain, tempe, kimchi halal
        """)
    st.divider()
    st.markdown("##### ⛔ Makanan HINDARI / BATASI - Risiko & Alternatif Aman")
    h1,h2 = st.columns(2)
    with h1:
        st.markdown("""
        **1. Sushi mentah, sashimi, kerang mentah**\n- Risiko: Anisakis, Listeria → keguguran, prematur\n- Alternatif: Sushi matang tempura, salmon panggang >63°C\n\n**2. Daging, ayam, telur setengah matang**\n- Risiko: Toksoplasma, Salmonella\n- Aman: Tidak ada pink, suhu >75°C\n\n**3. Susu mentah & keju lunak tidak pasteurisasi**\n- Risiko: Listeria\n- Cek: Harus ada pasteurized / UHT\n\n**4. Ikan merkuri tinggi: Hiu, Todak, King Mackerel, Tuna Bigeye**\n- Risiko: Merkuri rusak saraf & otak janin\n- Aman: Lele, salmon, kembung, nila, udang 200-300gr/mgg
        """)
    with h2:
        st.markdown("""
        **5. Kafein >200mg (~1 kopi kecil) & Energi drink**\n- Risiko: BBLR\n- Hitungan: Kopi 95mg, teh 47mg\n- Aman: Max 1 gelas kecil/hari\n\n**6. Alkohol 0 & Rokok / Vape 0**\n- Risiko: Fetal Alcohol Syndrome, BBLR, plasenta lepas\n\n**7. Jamu gendong tidak jelas, nanas muda & pepaya muda berlebihan**\n- Risiko: Kontraksi dini\n- Aman: Nanas matang 1-2 potong, pepaya matang\n\n**8. Ultra-processed tinggi garam, gula, soda**\n- Risiko: Hipertensi, preeklamsia, diabetes gestasional
        """)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[7]:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("#### ❓ Dokter + AI - FAQ Lengkap Per Trimester (Versi Super Lengkap)")
    st.markdown('<div class="disclaimer-box">⚠️ <b>DISCLAIMER:</b> Semua jawaban info UMUM & EDUKASI, bukan diagnosis pribadi. Untuk kepastian, WAJIB konsultasi dokter/bidan. Tanda bahaya (perdarahan banyak, ketuban pecah, gerakan &lt;10x/12jam, demam &gt;38.5, nyeri hebat) segera IGD.</div>', unsafe_allow_html=True)
    sub1, sub2 = st.tabs(["📝 Tracker Konsultasi", "💬 FAQ Lengkap + AI Dokter"])
    with sub1:
        st.caption("Tulis pertanyaan sebelum kontrol, biar gak lupa pas ketemu dokter")
        q = st.text_area("Pertanyaan", placeholder="Contoh: Apakah hasil lab saya normal?", key="q_tracker")
        a = st.text_area("Jawaban dokter (isi setelah kontrol)", placeholder="...", key="a_tracker")
        tgl = st.date_input("Tanggal", key="tgl_tracker")
        if st.button("Simpan Q&A"):
            data["faq_tracker"].append({"q": q, "a": a, "tgl": str(tgl)})
            save_all()
            st.success("Tersimpan!")
        for item in reversed(data["faq_tracker"][-20:]):
            st.markdown(f'<div style="background:#FFFCF8; border:1px solid #F0E6D8; border-radius:14px; padding:12px; margin-bottom:8px;"><b>Q:</b> {item["q"]}<br><b>A:</b> {item["a"]}<br><small>📅 {item["tgl"]}</small></div>', unsafe_allow_html=True)
    with sub2:
        st.markdown("##### ❓ FAQ Umum — Yang Selalu Ditanya Bumil (8 FAQ)")
        faqs_umum = [
            ("Apakah hasil lab saya normal?", "Hb normal >11 g/dL. Jika <11 anemia, tambah Fe. Gula puasa <92. Protein urine negatif normal, +1/+2 waspada preeklamsia. Gol darah penting antisipasi perdarahan."),
            ("Apakah BB saya naik sesuai?", "T1 naik 1-2kg total wajar. T2-T3 0.35-0.5kg/minggu. Total tergantung BMI: Kurus 12.5-18kg, Normal 11.5-16kg, Gemuk 7-11.5kg, Obesitas 5-9kg. Naik >1kg/minggu + bengkak + tensi naik = kontrol."),
            ("Vitamin apa yang perlu lanjut?", "T1: Folat+Vit D. T2: +Ca malam, Fe malam+Vit C, DHA siang. T3: Lanjut semua + Mg jika kram. Jangan stop tanpa dokter."),
            ("Boleh HB (hubungan suami-istri)?", "Boleh jika tidak flek, ketuban tidak rembes, tidak plasenta previa, dokter tidak larang. Posisi woman on top, side lying nyaman. Hindari jika flek, kontraksi, ketuban rembes."),
            ("Boleh naik pesawat?", "Aman sampai 28 minggu bebas, 28-36 butuh surat dokter, >36 ditolak maskapai. Hindari >4 jam, jalan tiap 1-2 jam, kaos kompresi, minum 250ml/jam."),
            ("Kapan kontrol berikutnya?", "T1 4 mingguan, T2 4 mingguan + USG anomali 20-22 minggu, T3 awal 2 mingguan + CTG, T3 akhir mingguan."),
            ("Apa yang harus diwaspadai?", "Perdarahan banyak, ketuban pecah banyak tidak bisa ditahan, gerakan <10x/12 jam, demam >38.5, muntah terus >24 jam, nyeri hebat, pusing + pandangan kabur + nyeri ulu hati."),
            ("Boleh cat rambut, skincare?", "T1 hindari dulu. T2-T3 boleh cat tanpa amonia ventilasi baik. Hindari retinol, hydroquinone, formalin. Aman: hyaluronic acid, niacinamide, mineral sunscreen."),
        ]
        for q,a in faqs_umum:
            with st.expander(f"• {q}"):
                st.write(a)

        st.markdown("##### 🌱 FAQ Trimester 1 (Minggu 0-13) - Awal Kehamilan (10 FAQ)")
        faqs_t1 = [
            ("Apakah mual berat sampai tidak bisa makan normal?", "Sangat umum di T1 karena hormon hCG naik. Tips: makan porsi kecil 5-6x, jangan biarkan lapar, biskuit kering sebelum bangun tidur, jahe hangat, hindari bau menyengat, vitamin B6 jika dokter saran. Waspada hyperemesis: jika muntah >5x/hari, tidak bisa minum >24 jam, BB turun >5%, urine pekat, segera ke IGD."),
            ("Flek kecoklatan sedikit di celana, bahaya?", "Bisa karena implantasi (hari ke 6-12 setelah pembuahan) atau perubahan hormon. Tapi tetap harus kontrol USG untuk pastikan bukan ancaman keguguran atau hamil di luar rahim. Istirahat, hindari HB & angkat berat."),
            ("Kapan detak jantung janin terdengar?", "Via USG transvaginal 6-7 minggu sudah terlihat, via USG perut 7-8 minggu. Via doppler 10-12 minggu. Jika di 8 minggu belum terlihat, dokter akan ulang 1 minggu lagi."),
            ("Kenapa sering pipis & sembelit?", "Rahim membesar menekan kandung kemih + hormon progesteron melambatkan usus. Tips: jangan tahan pipis, minum air tetap 2.3L tapi kurangi 2 jam sebelum tidur, makan serat 28gr, jalan kaki."),
            ("Kenapa mood swing, nangis tiba-tiba?", "Hormon estrogen & progesteron naik pesat. Wajar. Tips: tidur cukup 7-8 jam, cerita ke suami, journaling, prenatal yoga. Jika sedih terus >2 minggu, segera konsul."),
            ("Kapan USG pertama yang ideal?", "6-8 minggu untuk konfirmasi lokasi (dalam rahim bukan di luar), jumlah janin, dan DJJ. 11-13 minggu USG NT untuk screening Down syndrome."),
            ("Keputihan banyak, gatal?", "Keputihan putih susu tidak gatal & tidak bau = wajar karena hormon. Jika gatal, kuning hijau, bau amis, perih pipis, bisa infeksi yang harus diobati."),
            ("Boleh kerja berat, naik motor, nyetir?", "Kerja ringan boleh, hindari angkat >10kg, berdiri >3 jam nonstop. Naik motor boleh jika jalan halus & tidak jauh."),
            ("Boleh olahraga T1?", "Boleh ringan: jalan 20 menit, yoga T1, stretching. Hindari lari, lompat, angkat >5kg. Stop jika flek."),
            ("Makanan paling penting T1?", "Fokus folat & protein: bayam, brokoli, alpukat, telur matang, ayam, lele. Hindari sushi mentah, setengah matang, alkohol."),
        ]
        for q,a in faqs_t1:
            with st.expander(f"• {q}"):
                st.write(a)

        st.markdown("##### 🌸 FAQ Trimester 2 (14-27 Minggu) - Bulan Madu (10 FAQ)")
        faqs_t2 = [
            ("Kapan gerakan janin pertama terasa?", "Primigravida 18-22 minggu, multigravida 16-18 minggu. Rasanya seperti kupu-kupu, gelembung, kedutan halus. Jika sampai 24 minggu belum terasa, kontrol USG."),
            ("Sakit punggung, kram kaki tengah malam, wasir?", "Rahim membesar, beban bertambah, kalsium kurang. Tips: bantal hamil di antara kaki saat miring kiri, stretching betis sebelum tidur, kalsium 1000mg malam, magnesium 300mg jika saran dokter."),
            ("Posisi tidur terbaik?", "Miring kiri terbaik untuk aliran darah ke plasenta & janin. Miring kanan juga boleh. Hindari telentang lama >10 menit di T2 akhir-T3 karena rahim menekan vena cava."),
            ("Perut sering kencang-kencang, apakah kontraksi palsu?", "Bisa Braxton Hicks: tidak teratur, hilang jika istirahat/minum air. Kontraksi asli: teratur, makin kuat, makin sering. Jika kencang teratur <34 minggu + nyeri punggung, segera kontrol."),
            ("BB naik berapa ideal?", "Tergantung BMI awal: Kurus 12.5-18kg, Normal 11.5-16kg, Gemuk 7-11.5kg, Obesitas 5-9kg. T2 naik ~0.4kg/minggu."),
            ("Ngidam & tidak suka bau tertentu?", "Wajar karena hormon. Turuti ngidam selama makanan aman. Jika ngidam non-makanan (es batu banyak, tanah, kapur) disebut pica → bisa anemia, cek Hb."),
            ("Gusi berdarah, hidung mimisan, varises?", "Hormon bikin gusi sensitif & pembuluh darah melebar. Sikat gigi lembut, flossing, kontrol dokter gigi di T2."),
            ("Boleh traveling jauh naik mobil?", "Boleh di T2 (paling nyaman). Tips: berhenti tiap 2 jam jalan 10 menit, pakai seatbelt di bawah perut, bawa camilan & air, bawa buku KIA."),
            ("Boleh pijat hamil?", "Boleh >14 minggu terapis khusus bumil, posisi miring/duduk, hindari perut & titik tumit dalam."),
            ("Boleh puasa?", "Konsul dokter. Jika sehat, BB janin normal, tidak diabetes/anemia berat, boleh dengan sahur buka lengkap, minum 2.5L."),
        ]
        for q,a in faqs_t2:
            with st.expander(f"• {q}"):
                st.write(a)

        st.markdown("##### 🌙 FAQ Trimester 3 (28-40 Minggu) - Siap Lahiran (12 FAQ)")
        faqs_t3 = [
            ("Apa beda kontraksi asli vs palsu?", "PALSU: Tidak teratur, hilang istirahat/minum, hanya kencang di depan. ASLI: Teratur 10->5->3 menit, durasi 40-60 detik, makin kuat tidak hilang, ada lendir darah. Catat: jika 5-1-1 (5 menit sekali, 1 menit durasi, selama 1 jam) → ke RS."),
            ("Kapan harus ke RS? Tanda gawat darurat?", "SEGERA KE IGD jika: kontraksi 5-1-1, ketuban pecah banyak tidak bisa ditahan, perdarahan merah segar banyak, gerakan janin <10x/12 jam, demam >38°C, nyeri kepala hebat + pandangan kabur + bengkak mendadak (preeklamsia), nyeri ulu hati hebat."),
            ("Ketuban pecah warna hijau/kuning & bau, bahaya?", "Ketuban normal jernih agak putih. Jika hijau/kuning kental (meconium) → janin stress/BAB di dalam, kuning bau → infeksi. Segera ke RS, jangan tunggu kontraksi."),
            ("Posisi bayi sungsang / lintang, bisa muter?", "Masih bisa muter sampai 34-36 minggu. Tips: posisi knee-chest 15 menit 3x/hari, moxibustion, musik di bawah perut. Dokter bisa coba versi luar (ECV) di 36-37 minggu. Jika tetap sungsang, diskusi SC vs normal sungsang."),
            ("Boleh induksi alami? Jalan, squat, HB, makan nanas?", "Jalan kaki, squat, pelvic rocking boleh untuk bantu masuk panggul. HB boleh jika tidak kontraindikasi karena sperma mengandung prostaglandin. Stimulasi puting hati-hati. Nanas & kurma: bukti lemah, boleh secukupnya. Jangan jamu pelancar tidak jelas."),
            ("Perineal massage perlu? Bagaimana caranya?", "Bermanfaat kurangi robekan jalan lahir. Mulai 34-35 minggu, tiap malam 5-10 menit dengan minyak VCO/kelapa, pijat perlahan area perineum ke arah bawah & samping."),
            ("ASI belum keluar di hamil tua, normal?", "Normal. ASI pertama (kolostrum) baru banyak 2-3 hari setelah lahir. Yang penting IMD 1 jam pertama, skin to skin, hisapan bayi merangsang ASI."),
            ("Bengkak kaki & tangan, kapan waspada?", "Bengkak ringan sore hari di kaki wajar T3. Kurangi garam, angkat kaki, minum air cukup. WASPADA preeklamsia jika: bengkak mendadak di wajah/tangan, BB naik >1kg/minggu, TD >140/90, pusing hebat, pandangan kabur, nyeri ulu hati → segera ke RS."),
            ("Apa itu CTG & USG Doppler?", "CTG merekam DJJ & kontraksi, untuk cek kesejahteraan janin di T3, biasanya 36 minggu+. Doppler USG cek aliran darah plasenta & tali pusat, penting jika hipertensi, pertumbuhan kecil, lewat HPL."),
            ("Baby blues & persiapan mental?", "70% ibu alami baby blues hari 3-10 setelah lahir: nangis, cemas, lelah. Dukungan suami penting: bagi tugas, tidur saat bayi tidur, makan bergizi. Jika sedih >2 minggu, segera cari bantuan profesional."),
            ("Isi tas RS wajib?", "Ibu: KTP KK BPJS buku nikah KIA, baju kancing depan 3, pembalut nifas, underwear, bra, sandal, charger, camilan. Bayi: Baju 5, bedong 3, popok NB, topi, kaos kaki, tisu basah, selimut."),
            ("Lewat HPL belum lahiran?", "HPL perkiraan, normal 37-42 minggu. 40 minggu belum tanda cek CTG + USG ketuban. 41 minggu diskusi induksi. 42 minggu biasanya induksi karena plasenta menua."),
        ]
        for q,a in faqs_t3:
            with st.expander(f"• {q}"):
                st.write(a)

        st.divider()
        st.markdown("### 👩‍⚕️ Tanya AI Dokter OBGYN - Jawaban Umum (Edukasi)")
        st.markdown('<div class="disclaimer-box">💡 AI ini hanya untuk edukasi umum, bukan diagnosis pribadi. Ketik kata kunci seperti: mual, flek, kram, makanan, hb, pesawat, gerakan, lahiran, vitamin. Untuk kepastian, selalu konsultasi dokter langsung.</div>', unsafe_allow_html=True)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [{"role": "ai", "content": "Halo Bunda! 👋 Saya AI edukasi OBGYN. Saya bisa bantu jawab pertanyaan UMUM seputar kehamilan. Misalnya: 'Apakah mual berat normal di T1?', 'Makanan apa yang harus dihindari?', 'Kapan harus ke RS tanda persalinan?'. Tulis pertanyaan Bunda di bawah ya. Ingat ini info umum, untuk kepastian tetap konsultasi dokter langsung."}]
        kb = {
            "mual": "Mual muntah di T1 sangat umum karena hormon hCG. Tips: makan porsi kecil 5-6x/hari, jangan biarkan lapar, biskuit kering sebelum bangun, jahe hangat. Jika tidak bisa makan/minum >24 jam, muntah >5x/hari, BB turun, urine pekat → segera ke IGD, risiko dehidrasi.",
            "flek": "Flek kecoklatan sedikit di awal bisa karena implantasi atau perubahan hormon, tapi tetap harus kontrol USG untuk pastikan bukan ancaman keguguran atau hamil di luar rahim. Istirahat, hindari HB & angkat berat. Segera ke RS jika flek merah segar banyak, kram hebat.",
            "kram": "Kram perut ringan & kram kaki malam hari umum di T2-T3 karena rahim membesar, kurang kalsium & magnesium. Tips: stretching betis sebelum tidur, minum air 2.3L, kalsium 1000mg malam, magnesium 300mg jika dokter saran.",
            "makanan": "WAJIB: Protein 60-80gr (telur matang, ayam, lele/salmon 2x/mgg, tempe), Zat besi+Vit C (daging merah, hati ayam max 50gr/mgg, bayam+jeruk), Kalsium 1000mg (susu hamil 2 gelas), Serat (pepaya matang, pisang, oat), Air 2.3-2.5L. HINDARI: Sushi mentah, daging/telur setengah matang, susu mentah & keju lunak tidak pasteurisasi, ikan merkuri tinggi (hiu, todak, king mackerel, tuna bigeye), kafein >200mg, alkohol 0, rokok 0.",
            "hb": "Hubungan suami-istri boleh jika tidak ada kontraindikasi: tidak ada flek/perdarahan, ketuban tidak rembes, tidak plasenta previa total, tidak riwayat prematur/keguguran berulang, dan dokter tidak melarang. Pilih posisi nyaman (miring, woman on top).",
            "pesawat": "Umumnya aman sampai 28 minggu, 28-36 minggu butuh surat layak terbang. Tips: bawa surat dokter 7 hari sebelum terbang, pilih lorong, jalan tiap 1-2 jam, pakai kaos kompresi, minum 250ml/jam, hindari >4 jam. Hindari jika preeklamsia, ketuban pecah dini.",
            "gerakan": "Gerakan pertama 18-22 minggu (primigravida) seperti kupu-kupu/gelembung. T2 akhir tendangan jelas. T3 hitung gerakan: 10 gerakan dalam 12 jam. Jika mendadak berkurang, <10x/12 jam, segera ke RS untuk CTG.",
            "lahiran persalinan": "Tanda persalinan asli: kontraksi teratur 5 menit sekali, durasi 1 menit, selama 1 jam (5-1-1), makin kuat, ada lendir darah, ketuban pecah banyak tidak bisa ditahan. Segera ke RS jika 5-1-1, ketuban pecah, perdarahan, gerakan berkurang.",
            "vitamin": "T1: Folat 400-800mcg pagi + Vit D 600 IU pagi + B6 jika mual (resep). T2: +Kalsium 1000mg malam jauh Fe, Fe 27mg malam+Vit C, DHA 200-300mg siang. T3: lanjut Fe+Ca+DHA, Vit K minggu akhir jika saran dokter, Magnesium malam. Selalu konsul dokter untuk dosis personal.",
            "bengkak": "Bengkak kaki sore hari wajar T3. Tips: angkat kaki 15 menit tiap 2 jam, kurangi garam, minum air cukup, jangan berdiri lama. WASPADA jika bengkak mendadak wajah/tangan, BB naik >1kg/minggu, TD >140/90, pusing berat, pandangan kabur → risiko preeklamsia, segera ke IGD.",
        }
        def get_answer(q):
            ql = q.lower()
            for k,v in kb.items():
                if k in ql:
                    return v + "\n\nIni info umum ya Bunda, tiap kondisi bisa beda. Untuk kepastian diagnosis & penanganan, WAJIB konsultasi langsung ke dokter/bidan Bunda. Jika tanda bahaya, segera ke IGD."
            return "Pertanyaan bagus Bunda. Secara umum tiap kehamilan berbeda. Coba pakai kata kunci: mual, flek, kram, makanan, hb, pesawat, gerakan, lahiran, vitamin, bengkak. Saya akan jawab info umumnya. Ingat ini edukasi umum saja, untuk kepastian konsultasi dokter ya."
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        if prompt := st.chat_input("Ketik pertanyaan umum... misal: Apakah mual berat normal?"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            ans = get_answer(prompt)
            with st.chat_message("assistant"):
                st.write(ans)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            data["faq_tracker"].append({"q": prompt, "a": ans, "tgl": datetime.now().strftime("%Y-%m-%d %H:%M")})
            save_all()
        st.markdown("**Coba tanya cepat:**")
        c1,c2,c3,c4 = st.columns(4)
        if c1.button("Mual berat T1?"): st.session_state.chat_history.append({"role": "user", "content": "Apakah mual berat normal di trimester 1?"}); st.rerun()
        if c2.button("Boleh HB?"): st.session_state.chat_history.append({"role": "user", "content": "Bolehkah hubungan suami istri saat hamil?"}); st.rerun()
        if c3.button("Tanda ke RS?"): st.session_state.chat_history.append({"role": "user", "content": "Kapan harus ke RS tanda persalinan?"}); st.rerun()
        if c4.button("Makanan hindari?"): st.session_state.chat_history.append({"role": "user", "content": "Makanan apa yang harus dihindari ibu hamil?"}); st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="text-align:center; font-family:Caveat; font-size:18px; color:#9B8B7A; margin-top:30px;">"Setiap tendangan kecil adalah cerita besar" 🌸<br><small style="font-family:Poppins; font-size:11px;">Bumil Planner 280 Days — DIY Edition • Dibuat dengan cinta untuk ibu hebat • 2026</small></div>', unsafe_allow_html=True)
