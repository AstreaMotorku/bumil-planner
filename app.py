import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Bumil Planner 280 Days - Persistent", page_icon="🤰", layout="wide")

# Coba import gspread, kalau gagal fallback ke lokal
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    GSHEETS_AVAILABLE = True
except:
    GSHEETS_AVAILABLE = False

DATA_FILE_LOCAL = "bumil_data.json"

def default_data():
    return {
        "profil": {"nama_ibu": "", "nama_ayah": "", "hpht": "", "hpl": "", "gol_darah_ibu": "", "gol_darah_ayah": "", "rs_bidan": "", "hp_dokter": "", "bb_awal": "", "tb": "", "riwayat": ""},
        "kontrol": [{"tanggal": "", "usia": "", "td": "", "bb": "", "djj": "", "usg": "", "catatan": ""} for _ in range(10)],
        "bb_ibu": [], "bb_janin": [],
        "todo": {
            "T1 - Bulan 1 (Minggu 1-4)": [("Tes pack & catat HPHT", "Pagi hari", False), ("Hitung HPL", "HPHT+280", False), ("Mulai asam folat 400-800mcg", "Tiap pagi", False), ("Stop rokok/alkohol/kafein", "0 alkohol", False), ("Cek obat aman bumil", "Tanya dokter", False), ("Daftar dokter & buat KIA", "", False), ("Buat folder dokumen", "KK KTP BPJS", False), ("Cek BPJS aktif", "", False), ("Tidur 7-8 jam", "Miring kiri", False), ("Minum 2.3L/hari", "", False)],
            "T1 - Bulan 2 (Minggu 5-8)": [("USG pertama DJJ", "6-8 minggu", False), ("Lab darah lengkap", "Hb HIV HepB", False), ("Cek TSH tiroid", "", False), ("Atasi mual porsi kecil", "5-6x", False), ("Beli bra hamil", "", False), ("Catat BB mingguan", "Senin pagi", False), ("Hindari sushi mentah", "Listeria", False), ("Yoga ringan 15m", "", False)],
            "T1 - Bulan 3 (Minggu 9-13)": [("USG NT 11-13 / NIPT", "", False), ("Konsultasi hasil lab", "", False), ("Atur cuti hamil", "", False), ("Minyak anti stretch mark", "", False), ("List pertanyaan dokter T1", "", False), ("Financial plan", "", False), ("Bantal hamil", "", False), ("Hindari retinol", "", False)],
            "T2 - Bulan 4 (14-17)": [("USG anatomi awal", "", False), ("Kalsium & zat besi", "Saran dokter", False), ("Kelas hamil", "", False), ("Skincare bumil-friendly", "Hindari retinol", False), ("Tidur miring kiri", "", False), ("Baju hamil 2-3 stel", "", False), ("Jalan 20-30 menit", "", False), ("Ngobrol dengan janin", "", False)],
            "T2 - Bulan 5 (18-22)": [("USG anomali detail 20 minggu", "WAJIB", False), ("Cek Hb & gula darah", "", False), ("Catat gerakan janin", "Quickening", False), ("Riset pompa ASI & bouncer", "", False), ("Brainstorm nama bayi", "10 nama", False), ("Moodboard kamar bayi", "", False), ("Planning foto maternity", "", False)],
            "T2 - Bulan 6 (23-27)": [("TTGO 24-28 minggu", "", False), ("Vaksin Tdap & flu", "", False), ("Cek plasenta", "", False), ("Senam kegel", "3x10", False), ("Edukasi ASI", "", False), ("Draft birth plan", "", False), ("Cicil perlengkapan WAJIB 50%", "", False)],
            "T3 - Bulan 7 (28-31)": [("USG pertumbuhan doppler", "", False), ("Cek posisi kepala", "", False), ("Packing tas RS 70%", "", False), ("Kelas napas hypnobirthing", "", False), ("Berkas KTP KK BPJS", "Map khusus", False), ("Beli gendongan SSC & car seat", "", False), ("Finalisasi cuti", "", False)],
            "T3 - Bulan 8 (32-36)": [("Kontrol 2 mingguan", "", False), ("CTG & tanda bahaya", "", False), ("Finalisasi kamar & cuci baju bayi", "", False), ("Belajar mandikan bedong gendong", "", False), ("Sterilisasi botol pompa", "", False), ("Kontak darurat RS", "Tempel kulkas", False), ("Pengaman rumah", "", False)],
            "T3 - Bulan 9 (37-40)": [("Kontrol mingguan", "", False), ("Cek panggul", "", False), ("Packing tas RS 100%", "Baju ibu 3 bayi 5", False), ("Perineal massage", "", False), ("Latihan napas 4-7-8", "", False), ("Siaga tanda persalinan 5-1-1", "", False), ("Rute tercepat RS", "", False), ("Afirmasi positif", "", False), ("Stok frozen food", "2 minggu", False)],
        },
        "newborn": {
            "WAJIB PUNYA": [{"nama": "Popok kain 12pcs", "qty": 12, "harga": 0, "link": "", "ket": "Katun", "done": False}, {"nama": "Popok sekali pakai NB", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False}, {"nama": "Baju pendek 6 stel", "qty": 6, "harga": 0, "link": "", "ket": "Bambu", "done": False}, {"nama": "Bedong 6", "qty": 6, "harga": 0, "link": "", "ket": "", "done": False}, {"nama": "Perlak 2", "qty": 2, "harga": 0, "link": "", "ket": "Waterproof", "done": False}, {"nama": "Washlap 6 + Handuk 2", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False}, {"nama": "Sabun 2in1 + telon + cream ruam", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False}, {"nama": "Bak mandi lipat", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False}],
            "LUMAYAN PENTING": [{"nama": "Pompa ASI elektrik", "qty": 1, "harga": 0, "link": "", "ket": "Spectra", "done": False}, {"nama": "Sterilizer UV", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False}, {"nama": "Bouncer", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False}, {"nama": "Diaper bag", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False}, {"nama": "Gendongan SSC", "qty": 1, "harga": 0, "link": "", "ket": "CuddleMe", "done": False}],
            "TIDAK URGENT": [{"nama": "Sepatu bayi", "qty": 2, "harga": 0, "link": "", "ket": "", "done": False}, {"nama": "Stroller cabin", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False}, {"nama": "Car seat", "qty": 1, "harga": 0, "link": "", "ket": "", "done": False}]
        },
        "budget": [{"kategori": "Kontrol/USG", "nama": "USG + dokter", "estimasi": 500000, "aktual": 0, "lunas": False}, {"kategori": "Vitamin", "nama": "Vitamin 9 bulan", "estimasi": 1500000, "aktual": 0, "lunas": False}, {"kategori": "Bayi", "nama": "Perlengkapan wajib", "estimasi": 3000000, "aktual": 0, "lunas": False}, {"kategori": "Lahiran", "nama": "Biaya lahiran RS", "estimasi": 10000000, "aktual": 0, "lunas": False}],
        "vitamin_log": {}, "faq_tracker": []
    }

def load_local():
    if os.path.exists(DATA_FILE_LOCAL):
        try:
            with open(DATA_FILE_LOCAL, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default_data()
    return default_data()

def save_local(data):
    with open(DATA_FILE_LOCAL, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_gsheet_client():
    creds_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

def load_from_gsheet():
    try:
        client = get_gsheet_client()
        sheet_url = st.secrets["sheet_url"]
        sh = client.open_by_url(sheet_url)
        try:
            ws = sh.worksheet("data")
        except:
            ws = sh.add_worksheet(title="data", rows="1000", cols="20")
        val = ws.acell("A1").value
        if val and len(val) > 10:
            return json.loads(val)
        else:
            return default_data()
    except Exception as e:
        st.warning(f"Gagal load dari Google Sheets ({e}), pakai data lokal sementara")
        return load_local()

def save_to_gsheet(data):
    try:
        client = get_gsheet_client()
        sheet_url = st.secrets["sheet_url"]
        sh = client.open_by_url(sheet_url)
        try:
            ws = sh.worksheet("data")
        except:
            ws = sh.add_worksheet(title="data", rows="1000", cols="20")
        json_str = json.dumps(data, ensure_ascii=False)
        # Sheets cell limit 50k, chunk if needed
        if len(json_str) > 45000:
            # simpan terpecah di A1, A2, A3...
            ws.clear()
            chunks = [json_str[i:i+45000] for i in range(0, len(json_str), 45000)]
            for idx, chunk in enumerate(chunks):
                ws.update_acell(f"A{idx+1}", chunk)
            # simpan jumlah chunk di B1
            ws.update_acell("B1", str(len(chunks)))
        else:
            ws.update_acell("A1", json_str)
            ws.update_acell("B1", "1")
        # juga simpan lokal sebagai backup
        save_local(data)
        return True
    except Exception as e:
        st.error(f"Gagal simpan ke GSheet: {e}, simpan lokal saja")
        save_local(data)
        return False

# ---------- INIT DATA ----------
if "data" not in st.session_state:
    # cek apakah ada secrets gsheet -> pakai gsheet, kalau tidak pakai lokal
    if GSHEETS_AVAILABLE and "gcp_service_account" in st.secrets and "sheet_url" in st.secrets:
        st.session_state.use_gsheet = True
        st.session_state.data = load_from_gsheet()
    else:
        st.session_state.use_gsheet = False
        st.session_state.data = load_local()

data = st.session_state.data

# ---------- HEADER ----------
st.title("🤰 Bumil Planner 280 Days - Persistent Cloud")
if st.session_state.use_gsheet:
    st.success("✅ Mode Cloud Aktif - Data tersimpan di Google Sheets (anti hilang, bisa edit bareng istri)")
else:
    st.warning("⚠️ Mode Lokal - Data di bumil_data.json. Untuk Cloud permanen, setting Google Sheets di Secrets")

# ---------- TABS ----------
tabs = st.tabs(["👤 Profil", "✅ To-Do", "👶 Newborn", "💰 Budget", "💊 Vitamin", "❓ FAQ + AI Dokter"])

with tabs[0]:
    st.subheader("Profil")
    c1,c2 = st.columns(2)
    with c1:
        data["profil"]["nama_ibu"] = st.text_input("Nama Ibu", value=data["profil"]["nama_ibu"])
        data["profil"]["nama_ayah"] = st.text_input("Nama Ayah", value=data["profil"]["nama_ayah"])
        data["profil"]["hpht"] = st.text_input("HPHT YYYY-MM-DD", value=data["profil"]["hpht"])
        if data["profil"]["hpht"]:
            try:
                hpht = datetime.strptime(data["profil"]["hpht"], "%Y-%m-%d")
                hpl = hpht + timedelta(days=280)
                st.info(f"HPL: {hpl.strftime('%d %B %Y')} ({(hpl - datetime.now()).days} hari lagi)")
            except: pass
        data["profil"]["bb_awal"] = st.text_input("BB awal kg", value=data["profil"]["bb_awal"])
        data["profil"]["tb"] = st.text_input("TB cm", value=data["profil"]["tb"])
    with c2:
        data["profil"]["rs_bidan"] = st.text_input("RS/Bidan", value=data["profil"]["rs_bidan"])
        data["profil"]["hp_dokter"] = st.text_input("HP Dokter", value=data["profil"]["hp_dokter"])
        data["profil"]["riwayat"] = st.text_area("Riwayat", value=data["profil"]["riwayat"])

with tabs[1]:
    st.subheader("To-Do Super Lengkap - Centang gak bakal hilang")
    for bulan, tasks in data["todo"].items():
        with st.expander(f"{bulan} - {len([t for t in tasks if t[2]])}/{len(tasks)}"):
            for idx, (nama, ket, done) in enumerate(tasks):
                checked = st.checkbox(f"{nama} - {ket}", value=done, key=f"{bulan}_{idx}")
                if checked != done:
                    data["todo"][bulan][idx] = (nama, ket, checked)
                    if st.session_state.use_gsheet:
                        save_to_gsheet(data)
                    else:
                        save_local(data)
            new_t = st.text_input(f"Tambah tugas {bulan}", key=f"new_{bulan}")
            if st.button(f"Tambah ke {bulan}", key=f"btn_{bulan}") and new_t:
                data["todo"][bulan].append((new_t, "Custom", False))
                if st.session_state.use_gsheet: save_to_gsheet(data)
                else: save_local(data)
                st.rerun()

with tabs[2]:
    st.subheader("Newborn List + Harga + Link")
    for kat in ["WAJIB PUNYA", "LUMAYAN PENTING", "TIDAK URGENT"]:
        st.markdown(f"### {kat}")
        total = 0
        for i, item in enumerate(data["newborn"][kat]):
            with st.container(border=True):
                c1,c2 = st.columns([0.8,0.2])
                item["done"] = c1.checkbox(item["nama"], value=item["done"], key=f"{kat}_{i}_d")
                if c2.button("✕", key=f"del_{kat}_{i}"):
                    data["newborn"][kat].pop(i)
                    if st.session_state.use_gsheet: save_to_gsheet(data)
                    else: save_local(data)
                    st.rerun()
                item["qty"] = st.number_input("Qty", 1, 100, item["qty"], key=f"{kat}_{i}_q")
                item["harga"] = st.number_input("Harga Rp", 0, 10000000, item["harga"], key=f"{kat}_{i}_h")
                item["link"] = st.text_input("Link Shopee/Tokped", value=item["link"], key=f"{kat}_{i}_l")
                if item["link"]:
                    st.link_button("Buka Link", item["link"])
                item["ket"] = st.text_input("Ket", value=item["ket"], key=f"{kat}_{i}_k")
                total += item["harga"]*item["qty"]
        st.metric(f"Total {kat}", f"Rp {total:,}")
    st.divider()
    if st.button("💾 Simpan Semua Newborn"):
        if st.session_state.use_gsheet: save_to_gsheet(data)
        else: save_local(data)
        st.success("Tersimpan ke Cloud!" if st.session_state.use_gsheet else "Tersimpan lokal!")

with tabs[3]:
    st.subheader("Budget")
    edited = st.data_editor(data["budget"], num_rows="dynamic", use_container_width=True, key="budget")
    if st.button("Simpan Budget"):
        data["budget"] = edited
        if st.session_state.use_gsheet: save_to_gsheet(data)
        else: save_local(data)
        st.success("Tersimpan!")

with tabs[4]:
    st.subheader("Vitamin & Makanan Detail")
    st.info("""
    **T1:** Asam Folat 400-800mcg pagi, Vit D 600 IU pagi, B6 jika mual (resep dokter). Hindari Vit A >10.000 IU
    **T2:** +Kalsium 1000mg malam jauh zat besi, Zat besi 27mg malam+vit C, DHA 200-300mg siang, Magnesium 300mg malam
    **T3:** Lanjut zat besi+kalsium+DHA, Vit K minggu akhir jika disarankan
    """)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("**Wajib:** Protein 60-80gr (telur matang, ayam, lele/salmon, tempe), Zat besi+Vit C (hati ayam 1x/minggu max, daging merah, bayam+jeruk), Kalsium 1000mg (susu hamil 2 gelas), Serat (pepaya matang, pisang, oat), Air 2.3-2.5L")
    with c2:
        st.markdown("**Hindari:** Sushi mentah, daging/telur setengah matang, susu mentah & keju lunak tidak pasteurisasi, ikan merkuri tinggi Hiu/Todak/King Mackerel/Tuna Bigeye, kafein >200mg, alkohol 0, rokok 0, jamu tidak jelas")

with tabs[5]:
    st.subheader("FAQ + AI Dokter (Jawaban Umum)")
    st.warning("⚠️ AI ini hanya edukasi umum, BUKAN diagnosis. Untuk kepastian, konsultasi dokter langsung. Jika tanda bahaya (perdarahan banyak, ketuban pecah, gerakan janin <10x/12 jam, pusing berat), segera ke IGD.")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "ai", "content": "Halo Bunda! Saya AI edukasi OBGYN. Tanya apa saja tentang kehamilan umum (mual, vitamin, makanan, tanda lahiran). Saya jawab info umum ya, untuk kepastian tetap ke dokter."}]
    
    # knowledge base simple
    kb = {
        "mual": "Mual trimester 1 normal karena hormon hCG naik. Tips umum: makan porsi kecil 5-6x, biskuit sebelum bangun, hindari bau menyengat, jahe hangat. Jika tidak bisa makan/minum >24 jam, muntah terus, BB turun, segera kontrol.",
        "flek": "Flek sedikit di awal bisa karena implantasi, tapi tetap harus kontrol untuk pastikan bukan ancaman keguguran. Hindari HB dulu, istirahat, dan segera USG jika flek banyak, darah segar, atau kram hebat.",
        "boleh hb": "Boleh berhubungan jika tidak ada kontraindikasi: tidak ada flek, ketuban tidak rembes, tidak ada plasenta previa, dan dokter tidak melarang. Pilih posisi nyaman, komunikasi dengan pasangan.",
        "pesawat": "Umumnya aman sampai 28-36 minggu dengan surat dokter. Hindari penerbangan >4 jam, jalan tiap 1-2 jam, pakai kaos kompresi, minum cukup.",
        "makanan": "Wajib: protein 60-80gr, zat besi+vit C, kalsium 1000mg, serat, air 2.3L. Hindari: sushi mentah, daging/telur setengah matang, susu mentah, ikan merkuri tinggi (hiu, todak, king mackerel), kafein >200mg, alkohol 0, rokok 0.",
        "lahiran": "Tanda persalinan asli: kontraksi teratur 5 menit sekali durasi 1 menit selama 1 jam (5-1-1), lendir darah, ketuban pecah (banyak, tidak bisa ditahan). Segera ke RS jika 5-1-1, ketuban pecah, perdarahan, gerakan janin berkurang.",
        "gerakan": "Gerakan janin halus mulai 18-22 minggu (quickening). Di T3, hitung 10 gerakan dalam 12 jam. Jika <10 gerakan atau mendadak berkurang, segera ke RS.",
        "vitamin": "Umum: T1 asam folat 400-800mcg + vit D 600 IU. T2 tambah kalsium 1000mg malam, zat besi 27mg malam+vit C, DHA 200-300mg siang. T3 lanjut. Selalu konsul dokter untuk dosis pribadi."
    }

    def get_ai_answer(q):
        ql = q.lower()
        for k,v in kb.items():
            if k in ql:
                return v + "\n\nIni info umum ya, tiap kondisi bisa beda. Untuk kepastian, konsultasi langsung ke dokter/bidan Bunda."
        return "Pertanyaan bagus. Secara umum, kondisi tiap ibu hamil berbeda. Coba tanyakan dengan kata kunci: mual, flek, boleh hb, pesawat, makanan, tanda lahiran, gerakan janin, vitamin. Ingat ini info umum saja, untuk kepastian konsultasi dokter ya."

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Ketik pertanyaan umum... misal: Apakah mual berat normal?"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        ans = get_ai_answer(prompt)
        st.session_state.chat_history.append({"role": "ai", "content": ans})
        with st.chat_message("ai"):
            st.write(ans)
        # auto save riwayat ke data
        data["faq_tracker"].append({"q": prompt, "a": ans, "tgl": datetime.now().strftime("%Y-%m-%d %H:%M")})
        if st.session_state.use_gsheet: save_to_gsheet(data)
        else: save_local(data)

# ---------- SIDEBAR SAVE ----------
st.sidebar.divider()
if st.sidebar.button("💾 Simpan Semua ke Cloud Sekarang"):
    if st.session_state.use_gsheet:
        save_to_gsheet(data)
        st.sidebar.success("Tersimpan di Google Sheets!")
    else:
        save_local(data)
        st.sidebar.success("Tersimpan lokal!")

if st.sidebar.button("🔄 Load Ulang dari Cloud"):
    if st.session_state.use_gsheet:
        st.session_state.data = load_from_gsheet()
        st.rerun()

st.sidebar.caption("Data disimpan di Google Sheets jika secrets ada, kalau tidak di bumil_data.json. Jadi kalau lu isi malam ini, besok masih ada dan bisa diedit bareng istri.")
