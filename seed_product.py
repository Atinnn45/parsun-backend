from Database import get_connection, init_db

init_db()
conn = get_connection()
cursor = conn.cursor()

# Ambil category IDs
cursor.execute("SELECT id, name FROM categories")
categories = {row['name']: row['id'] for row in cursor.fetchall()}

print("Kategori tersedia:", categories)

# ===================== DATA PRODUK =====================
products = [

    # ===== PARSUN =====
    ("PSN-F15", "Mesin Tempel Parsun F15 BMS 15HP 4-Tak", 18500000, 5, "Mesin", "Parsun",
     "Mesin tempel 4-tak 15HP, cocok untuk perahu nelayan dan speedboat kecil. Irit bahan bakar, bertenaga, dan mudah perawatan. Dilengkapi sistem pendingin air dan tuas mundur."),
    ("PSN-F9.9", "Mesin Tempel Parsun F9.9 BMS 9.9HP 4-Tak", 12800000, 7, "Mesin", "Parsun",
     "Mesin tempel 4-tak 9.9HP. Ringan dan efisien untuk perahu ukuran sedang. Konsumsi bahan bakar sangat irit."),
    ("PSN-F6", "Mesin Tempel Parsun F6 BMS 6HP 4-Tak", 8900000, 10, "Mesin", "Parsun",
     "Mesin tempel 4-tak 6HP untuk perahu kecil dan sampan. Mudah distart, ringan dibawa."),
    ("PSN-F30", "Mesin Tempel Parsun F30 BMS 30HP 4-Tak", 34000000, 3, "Mesin", "Parsun",
     "Mesin tempel 4-tak 30HP bertenaga tinggi. Ideal untuk kapal nelayan ukuran besar dan speedboat."),
    ("PSN-F5", "Mesin Tempel Parsun F5 BMS 5HP 4-Tak", 7200000, 8, "Mesin", "Parsun",
     "Mesin tempel 4-tak 5HP. Paling ringan di kelasnya, cocok untuk perahu dayung bermotor."),

    # Sparepart Parsun
    ("PSN-SP-001", "Busi NGK B7HS untuk Mesin Parsun 2-Tak", 45000, 100, "Sparepart", "Parsun",
     "Busi original NGK B7HS kompatibel untuk mesin Parsun 2-tak 5HP-15HP. Garansi keaslian produk."),
    ("PSN-SP-002", "Filter Oli Mesin Parsun F15/F20 4-Tak", 125000, 50, "Sparepart", "Parsun",
     "Filter oli original untuk mesin Parsun 4-tak seri F15 dan F20. Ganti setiap 100 jam pemakaian."),
    ("PSN-SP-003", "Impeller Water Pump Parsun F15", 185000, 30, "Sparepart", "Parsun",
     "Impeller pompa air pendingin untuk Parsun F15. Material karet berkualitas tinggi tahan air laut."),
    ("PSN-SP-004", "Karburator Lengkap Parsun F5/F6", 450000, 20, "Sparepart", "Parsun",
     "Karburator complete assembly untuk Parsun F5 dan F6. Sudah include jarum pelampung dan gasket."),
    ("PSN-SP-005", "Propeller 3 Daun Parsun F15 (13 Pitch)", 350000, 25, "Sparepart", "Parsun",
     "Baling-baling 3 daun aluminium alloy untuk Parsun F15. Pitch 13, diameter 9.25 inci."),
    ("PSN-SP-006", "Anoda Zinc Parsun F9.9/F15", 85000, 60, "Sparepart", "Parsun",
     "Zinc anode pelindung korosi untuk Parsun F9.9 dan F15. Wajib diganti rutin untuk menjaga mesin dari karat."),
    ("PSN-SP-007", "Gasket Set Parsun F15 Full Set", 320000, 15, "Sparepart", "Parsun",
     "Set gasket lengkap untuk overhaul mesin Parsun F15. Termasuk head gasket, base gasket, dan semua O-ring."),
    ("PSN-SP-008", "Tali Starter Parsun F6/F9.9", 55000, 80, "Sparepart", "Parsun",
     "Tali starter recoil untuk Parsun F6 dan F9.9. Panjang 2.5m, diameter 4mm, material nylon kuat."),
     ("PSN-SP-009", "O-Ring Kit Parsun T36 Series", 85000, 40, "Sparepart", "Parsun",
     "O-ring kit Parsun untuk sealing mesin. Tahan panas dan tekanan tinggi."),
    ("PSN-SP-010", "Seal Kit Parsun T40 Series", 95000, 35, "Sparepart", "Parsun",
     "Seal kit Parsun untuk mencegah kebocoran oli dan air."),
    ("PSN-SP-011", "Bearing Parsun Engine", 125000, 20, "Sparepart", "Parsun",
     "Bearing mesin Parsun original untuk sistem rotating engine."),
    ("PSN-SP-012", "Gasket Parsun Engine Set", 135000, 25, "Sparepart", "Parsun",
     "Gasket Parsun untuk perbaikan mesin dan overhaul."),

    # ===== YAMAHA MARINE =====
    ("YMH-F15", "Mesin Tempel Yamaha F15CMHS 15HP 4-Tak", 24500000, 4, "Mesin", "Yamaha Marine",
     "Mesin tempel Yamaha 4-tak 15HP terbaru. Teknologi multi-function tiller handle, irit BBM, bertenaga. Garansi resmi Yamaha."),
    ("YMH-F25", "Mesin Tempel Yamaha F25LMHS 25HP 4-Tak", 31000000, 3, "Mesin", "Yamaha Marine",
     "Mesin tempel Yamaha 25HP 4-tak dengan sistem injeksi. Tenaga besar, getaran minimal, cocok untuk speedboat."),
    ("YMH-F40", "Mesin Tempel Yamaha F40FETL 40HP 4-Tak", 52000000, 2, "Mesin", "Yamaha Marine",
     "Mesin tempel Yamaha 40HP 4-tak injeksi. Performa tinggi untuk kapal nelayan dan leisure boat."),

    # Sparepart Yamaha
    ("YMH-SP-001", "Busi NGK DCPR6E untuk Yamaha 4-Tak F15/F25", 65000, 80, "Sparepart", "Yamaha Marine",
     "Busi original NGK DCPR6E untuk mesin Yamaha 4-tak seri F15, F20, F25. Performa pengapian optimal."),
    ("YMH-SP-002", "Filter BBM Yamaha F15-F40 Outboard", 95000, 40, "Sparepart", "Yamaha Marine",
     "Filter bahan bakar inline untuk mesin Yamaha 4-tak. Mencegah kotoran masuk ke karburator/injektor."),
    ("YMH-SP-003", "Impeller Yamaha F15/F20 6H3-WB103", 245000, 25, "Sparepart", "Yamaha Marine",
     "Impeller pompa air original Yamaha part number 6H3-WB103. Untuk F15 dan F20. Ganti setiap 2 tahun."),
    ("YMH-SP-004", "Propeller Yamaha 3 Daun 9.25x10 F15/F20", 520000, 15, "Sparepart", "Yamaha Marine",
     "Propeller aluminium alloy original Yamaha untuk F15/F20. Ukuran 9.25x10, 3 daun, spline 13."),
    ("YMH-SP-005", "Gear Oil Yamalube Outboard 90mL", 45000, 150, "Sparepart", "Yamaha Marine",
     "Oli gardan/lower unit original Yamalube SAE90 untuk semua mesin tempel Yamaha. Kemasan 90mL sachet."),
    ("YMH-SP-006", "Anoda Zinc Yamaha F15/F25 6G1-45251", 110000, 50, "Sparepart", "Yamaha Marine",
     "Zinc anode original Yamaha part no 6G1-45251. Untuk F15 dan F25. Lindungi lower unit dari korosi air laut."),
    ("YMH-SP-007", "Thermostat Yamaha F15/F20 67C-12411", 185000, 20, "Sparepart", "Yamaha Marine",
     "Thermostat original Yamaha untuk F15 dan F20. Menjaga suhu mesin tetap optimal. Part no 67C-12411."),
    ("YMH-SP-008", "Fuel Filter Yamaha MS S3227", 95000, 20, "Sparepart", "Yamaha Marine",
     "Filter bahan bakar Yamaha untuk menjaga kebersihan sistem fuel."),
    ("YMH-SP-009", "Water Separator Filter Yamaha", 120000, 15, "Sparepart", "Yamaha Marine",
     "Filter dengan water separator untuk mesin Yamaha."),

    # ===== SUZUKI MARINE =====
    ("SZK-DF15", "Mesin Tempel Suzuki DF15AS 15HP 4-Tak", 26000000, 3, "Mesin", "Suzuki Marine",
     "Mesin tempel Suzuki 4-tak 15HP. Teknologi Lean Burn dan Offset Driveshaft untuk efisiensi BBM terbaik di kelasnya."),
    ("SZK-DF9.9", "Mesin Tempel Suzuki DF9.9AS 9.9HP 4-Tak", 19500000, 4, "Mesin", "Suzuki Marine",
     "Mesin tempel Suzuki DF9.9 4-tak, ringan dan bertenaga. Dilengkapi tilt system untuk kemudahan operasional."),

    # Sparepart Suzuki


    # ===== HONDA MARINE =====


    # Sparepart Honda


    # ===== MERCURY MARINE =====
    ("MCR-F15", "Mesin Tempel Mercury F15ML EFI 15HP 4-Tak", 28500000, 2, "Mesin", "Mercury Marine",
     "Mesin tempel Mercury 15HP dengan sistem EFI (Electronic Fuel Injection). Performa tinggi, start mudah dalam kondisi apapun."),

    # Sparepart Mercury
    ("MCR-SP-001", "Impeller Mercury 40-60HP 47-43026Q06", 275000, 15, "Sparepart", "Mercury Marine",
     "Impeller pompa air Mercury untuk mesin 40-60HP. Part no 47-43026Q06. Kualitas original."),
    ("MCR-SP-002", "Propeller Mercury Spitfire 10x13 3 Daun", 650000, 8, "Sparepart", "Mercury Marine",
     "Propeller Mercury Spitfire aluminium 3 daun 10x13. Performa akselerasi terbaik untuk speedboat."),
    ("MCR-SP-003", "Oil Filter Mercury 35-881126K01", 185000, 25, "Sparepart", "Mercury Marine",
     "Filter oli original Mercury 35-881126K01 untuk mesin Mercruiser. Menjaga performa mesin tetap optimal dan bersih."),
    ("MCR-SP-004", "Fuel Filter Mercury 35-8M0062950", 210000, 20, "Sparepart", "Mercury Marine",
     "Filter bahan bakar Mercury original 35-8M0062950. Mencegah kotoran masuk ke sistem injeksi mesin."),
    ("MCR-SP-005", "Fuel Filter Quicksilver 35-8M0148584", 195000, 20, "Sparepart", "Mercury Marine",
     "Filter BBM Quicksilver original untuk mesin Mercury. Kualitas tinggi dan tahan lama."),
    ("MCR-SP-006", "Bearing Carrier Assy Mercury 41641A8", 950000, 5, "Sparepart", "Mercury Marine",
     "Bearing carrier assembly Mercury original part 41641A8 untuk sistem gear lower unit."),
    ("MCR-SP-007", "Oil Pump Mercury 897206T03", 1250000, 4, "Sparepart", "Mercury Marine",
     "Pompa oli Mercury original 897206T03. Menjaga sirkulasi oli mesin tetap stabil."),
    ("MCR-SP-008", "Sprocket Cam Drive Mercury 43-880550", 850000, 6, "Sparepart", "Mercury Marine",
     "Sprocket cam drive Mercury original untuk sistem timing mesin."),
    ("MCR-SP-009", "Prop Hub Assembly Kit Mercury Racing", 650000, 10, "Sparepart", "Mercury Marine",
     "Kit hub propeller Mercury Racing. Mendukung performa maksimal pada propeller."),
    ("MCR-SP-010", "Clutch Mercury 52-8M0094479", 780000, 12, "Sparepart", "Mercury Marine",
     "Komponen clutch Mercury original untuk sistem transmisi lower unit."),
    ("MCR-SP-011", "Ignition Coil Quicksilver 8M0077471", 450000, 10, "Sparepart", "Mercury Marine",
     "Koil pengapian Quicksilver untuk mesin Mercury. Stabil dan tahan lama."),
    ("MCR-SP-012", "Fuel Pump Kit Mercury 881705T1", 550000, 8, "Sparepart", "Mercury Marine",
     "Fuel pump kit Mercury original untuk suplai bahan bakar optimal."),
    ("MCR-SP-013", "Piston Assembly Mercury 700-8M0075695", 950000, 6, "Sparepart", "Mercury Marine",
     "Piston assembly Mercury untuk performa mesin maksimal."),
    ("MCR-SP-014", "Gear Set Forward Mercury 43-8M0078258", 1250000, 5, "Sparepart", "Mercury Marine",
     "Gear forward Mercury untuk sistem transmisi lower unit."),
    ("MCR-SP-015", "Gear Set Reverse Mercury 43-8M0053121", 1250000, 5, "Sparepart", "Mercury Marine",
     "Gear reverse Mercury original untuk sistem gigi mundur mesin tempel."),
    ("MCR-SP-016", "Extreme Grease Quicksilver NLGI 2", 95000, 30, "Sparepart", "Mercury Marine",
     "Grease high performance Quicksilver untuk pelumasan komponen mesin dan propeller."),
    ("MCR-SP-017", "Marine Grease 2-4-C Quicksilver", 90000, 30, "Sparepart", "Mercury Marine",
     "Grease marine tahan air laut untuk semua komponen mesin tempel."),
    ("MCR-SP-018", "Corrosion Guard Spray Quicksilver", 110000, 25, "Sparepart", "Mercury Marine",
     "Spray anti karat Quicksilver untuk perlindungan komponen logam."),
    ("MCR-SP-019", "Power Tune Spray Quicksilver", 115000, 25, "Sparepart", "Mercury Marine",
     "Cleaner internal mesin untuk membersihkan carbon deposit."),
    ("MCR-SP-020", "Water Separating Fuel Filter Moeller", 175000, 20, "Sparepart", "Mercury Marine",
     "Filter BBM dengan water separator untuk menjaga mesin dari air dan kotoran."),

    # ===== OMAX MARINE (AKSESORIS UMUM) =====

]

# ===================== INSERT PRODUK =====================
inserted = 0
updated = 0
skipped = 0

for code, name, price, stock, ptype, cat_name, desc in products:
    # Cek apakah produk sudah ada
    cursor.execute("SELECT id FROM products WHERE product_code = ?", (code,))
    existing = cursor.fetchone()
    
    cat_id = categories.get(cat_name)
    if not cat_id:
        print(f"  [WARN] Kategori '{cat_name}' tidak ditemukan, skip: {name[:40]}")
        skipped += 1
        continue
    
    if existing:
        # UPDATE existing product
        cursor.execute("""
            UPDATE products 
            SET name=?, price=?, stock=?, product_type=?, category_id=?, description=?, sold=0
            WHERE product_code=?
        """, (name, price, stock, ptype, cat_id, desc, code))
        print(f"  [UPDATE] {code} - {name[:40]}")
        updated = updated + 1 if 'updated' in locals() else 1
    else:
        # INSERT new product
        cursor.execute("""
            INSERT INTO products (product_code, name, price, stock, sold, product_type, category_id, description, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (code, name, price, stock, 0, ptype, cat_id, desc, None))
        print(f"  [INSERT] {code} - {name[:50]}")
        inserted += 1

    if 'updated' not in locals():
        updated = 0

conn.commit()
conn.close()

print(f"\n✅ Selesai! {inserted} produk berhasil ditambahkan, {skipped} dilewati.")