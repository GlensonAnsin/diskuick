"""Indonesian strings, in the order of i18n_keys.KEYS. Best-effort translation - please have a native speaker review."""
from i18n import register_seq

register_seq("id", "Bahasa Indonesia", (
    "Dasbor", "Game", "Alat", "Pengaturan",                                                            # 1-5
    "Menjaga drive Anda tetap aktif saat bermain",
    "Tersendat terbaru", "Kesehatan drive", "Cek lag", "Benchmark & penyetelan otomatis",
    "Perilaku", "Tampilan", "Kapan dijalankan", "Intensitas default",                                  # 10-14
    "Latensi baca langsung",
    "Aktif", "Menunggu", "Mati", "Galat", "Dinonaktifkan", "Siaga", "Memulai",                         # 16-22
    "Dijeda saat memakai baterai",
    "Pilih drive di Pengaturan", "Tambahkan game di tab Game",
    "Menunggu game dimulai", "Menunggu jendela game difokuskan",
    "Dijaga aktif", "Sesi", "Tersendat tercatat", "Diaktifkan",                                        # 28-31
    "Belum ada tersendat yang tercatat.",
    "Setiap titik adalah pembacaan paling lambat dalam detik itu. Lonjakan di atas garis merah adalah tersendat: saat drive ragu-ragu.",
    "Mulai game (atau pilih “Selalu aktif”) untuk melihat latensi langsung.",
    "Menunggu data...",
    "tersendat", "sekarang", "Pembaruan tersedia", "Unduh",                                            # 36-39
    "Deteksi game terpasang", "Memindai...", "Tambah program yang berjalan…",
    "atau ketik nama program, mis. game.exe",
    "Tambah", "Drive", "Intensitas", "Default",                                                        # 44-47
    "Belum ada game.\nKlik “Deteksi game terpasang” untuk menemukannya otomatis.",
    "Pilih program yang berjalan", "Buka game Anda dulu, lalu pilih di sini.",
    "Cari...", "Tidak ditemukan", "Game terdeteksi", "Tidak ada game baru ditemukan.",                 # 51-54
    "Mencari di Steam, Epic Games, dan GOG. Anda tetap bisa menambah game lewat “Tambah program yang berjalan” atau dengan mengetik nama exe-nya.",
    "Pilih game yang drive-nya ingin dijaga tetap aktif.",
    "Nama program adalah tebakan terbaik: periksa jika game tidak terpicu.",
    "Pilih semua", "Tambah yang dipilih", "Tutup",                                                     # 58-60
    "Drive yang diperiksa", "Segarkan", "Mulai ulang sebagai administrator", "Membaca info drive...",
    "Yang diketahui Windows tentang drive ini, dengan saran berbahasa sederhana.",
    "Kesehatan", "Suhu", "Keausan", "Waktu menyala", "t/a",                                            # 66-70
    "{free} GB kosong dari {total} GB",
    "Mengukur berapa lama pembacaan pertama setelah drive menganggur, dengan dan tanpa penjagaan aktif, lalu memilih pengaturan teringan yang membantu. Memakan waktu sekitar 2 menit. Jangan jalankan game selama itu.",
    "Jalankan penyetelan otomatis", "Menyiapkan…", "Batal", "Dibatalkan.", "Tes gagal",                # 73-77
    "Penjagaan aktif", "ms rata-rata", "ms p95", "ms maks", "Tidak ada",                               # 78-82
    "Penjagaan aktif menghilangkan tersendat saat menganggur. Pengaturan yang disarankan: {p}.",
    "Tidak ada tersendat saat menganggur pada drive ini: bangunnya cepat. Penjagaan aktif mungkin tidak membantu di sini.",
    "Drive ini ragu-ragu setelah menganggur, tetapi penjagaan aktif tidak jelas membantu. Penyebabnya mungkin di tempat lain: coba Cek lag.",
    "Gunakan {p} sebagai default", "Tersimpan.",                                                       # 86-87
    "Pindah ke game Anda tepat setelah menekan Mulai. Setelah 10 detik, Diskuick mengamati disk, CPU, dan memori asli Anda selama 30 detik dan memberi tahu apa yang tampak salah.",
    "Mulai cek lag", "Mulai dalam {s} dtk: pindah ke game Anda sekarang…", "Mengukur… teruskan bermain",
    "Hanya indikatif: jaringan tidak diukur.",
    "Hanya saat bermain", "Selalu aktif",                                                              # 93-94
    "Mulai otomatis saat salah satu game Anda terbuka dan berhenti saat ditutup. Tambahkan game di tab Game.",
    "Berjalan selama Diskuick terbuka. Sederhana, tetapi drive tetap sibuk bahkan saat menganggur.",
    "Drive yang dijaga aktif",
    "Seberapa kuat drive disentuh. Game dapat menimpa ini.",
    "Ringan", "Seimbang", "Berat",                                                                     # 99-101
    "Pembacaan acak kecil, sekitar 10 per detik. Beban paling sedikit: coba ini dulu.",
    "Pembacaan sekuensial ringan, sekitar 20 per detik. Untuk drive yang butuh sedikit lebih.",
    "Pembacaan tanpa henti. Efek terkuat, tetapi drive selalu sibuk.",
    "Detik antar pembacaan (lanjutan)", "default",                                                     # 105-106
    "Masukkan angka positif, atau kosongkan untuk default.",
    "Jeda saat memakai baterai", "Laptop: jangan buat drive sibuk saat tidak tercolok.",
    "Hanya saat game difokuskan", "Dijeda saat Anda alt-tab keluar dari game.",
    "Beri tahu saat game dimulai", "Notifikasi kecil di baki sistem.",
    "Mulai bersama Windows", "Berjalan diam-diam di baki sistem saat masuk.",
    "Tema", "Sistem", "Gelap", "Tema terang", "Bahasa",                                                # 116-120
    "Periksa pembaruan",
    "Hanya nama repositori yang dihubungi; tidak ada data tentang Anda yang dikirim.",
    "Pemeriksaan pembaruan nonaktif sampai repositori rilis ditetapkan.",
    "Buka folder data", "Buka log tersendat",
    "Intensitas pintar aktif: ia memilih level untuk Anda. Matikan untuk memilih sendiri.",
    "Pintar",                                                                                          # 127
    "Mulai ulang sebagai administrator untuk pemindaian cepat",
    "Menampilkan apa yang memakan ruang, dari yang terbesar. Tidak ada yang diubah atau dihapus di sini. Sebagai administrator, ia membaca tabel file drive langsung (seperti WizTree) dalam hitungan detik; jika tidak, ia membaca folder satu per satu, yang bisa memakan satu atau dua menit.",
    "Memakan {s} dtk.", "Ganti nama game", "Nama yang ditampilkan untuk",                           # 130-132
    "Overlay latensi",
    "Tampilan langsung kecil di sudut layar selama drive dijaga aktif (ada game berjalan, atau Selalu aktif). Ini jendela terpisah yang tidak pernah menyentuh game, dan tampil di atas game berjendela dan tanpa batas. Tidak bisa tampil di atas layar penuh eksklusif (misalnya Battlefield 3): ubah game itu ke tanpa batas atau berjendela.",
    "Tampilkan overlay saat game berjalan", "Posisi", "Pratinjau",                                    # 135-137
    "Kiri atas", "Kanan atas", "Kiri bawah", "Kanan bawah",
    "Perbarui sekarang", "Mengunduh… {p}%", "Pembaruan gagal", "Coba lagi", "Periksa sekarang",        # 142-146
    "Memeriksa…", "Anda sudah yang terbaru.", "Tidak dapat memeriksa pembaruan.", "Pembaruan tersedia: {v}",
    "Buka Diskuick", "Keluar", "Menjaga drive {d}: tetap aktif",                                       # 151-153
    "Tidak dapat mengubah pengaturan startup",
    "Sesi terakhir", "Apakah drive-nya? Ringkasan sesi bermain terakhir Anda.",
    "Belum ada sesi tercatat. Laporan muncul saat game ditutup.",
    "Pembacaan terburuk", "tersendat", "puncak", "ping",                                               # 158-161
    "Tanda lag",
    "Tekan Ctrl+Alt+L (atau pakai menu baki) saat game lag. Diskuick menyimpan apa yang sedang dikerjakan PC saat itu.",
    "Belum ada lag yang ditandai.", "Tandai lag sekarang", "Lag ditandai", "Sesi berakhir",            # 162-167
    "Ditutup untuk membebaskan sumber daya", "Intensitas pintar",
    "Mulai dari Ringan dan naik hanya saat drive terus tersendat, lalu turun lagi saat tenang. Mengabaikan pilihan di atas (pengaturan milik game tetap menang).",
    "Peringatan drive", "Beri tahu saya saat drive game hampir penuh atau tidak lagi sehat.",          # 171-172
    "Pintasan keyboard",
    "Ctrl+Alt+L menandai momen lag. Ctrl+Alt+O menampilkan atau menyembunyikan overlay.",
    "Tampilkan overlay saat drive dijaga aktif",
    "Tampilkan juga beban CPU dan GPU", "Tampilkan juga FPS",                                          # 176-177
    "Perlu PresentMon.exe di samping Diskuick.exe dan Diskuick berjalan sebagai administrator.",
    "Cek jaringan (opsional)",
    "Memeriksa apakah internet Anda bisa menjadi penyebab lag. Ketik 1.1.1.1 untuk memeriksa koneksi umum Anda, atau alamat server tempat Anda bermain (:port bersifat opsional dan default-nya 443). Selama Cek lag (dan saat Anda menandai lag), Diskuick mengukur ping (berapa lama server menjawab) dan kehilangan paket (jawaban yang tidak pernah tiba), sehingga Anda bisa membedakan masalah jaringan dari masalah drive. Hanya koneksi biasa yang dibuka, beberapa kali per detik, dan tidak ada data tentang Anda yang dikirim. Kosongkan untuk menonaktifkan.",
    "Host", "Masukkan nama host atau alamat, opsional dengan :port.",
    "Mode game (opsional)",
    "Saat salah satu game Anda dimulai, meminta program-program ini dengan sopan untuk menutup (mereka masih bisa meminta Anda menyimpan) dan membukanya lagi saat game selesai. Tidak ada yang ditutup paksa.",
    "Belum ada program dipilih.", "Hapus", "Program itu dilindungi dan tidak dapat ditutup.",          # 185-187
    "Buka lagi sesudahnya", "Disk", "Drive yang dianalisis", "Pindai", "Berhenti", "Menghentikan...", "Naik", # 188-194
    "Nama", "Ukuran", "File", "% dari induk", "Buka di Explorer", "Buka folder ini di sini",           # 195-200
    "Penganalisis ruang disk",
    "Menampilkan apa yang memakan ruang, dari yang terbesar. Ia membaca folder satu per satu, jadi drive besar memakan satu atau dua menit. Tidak ada yang diubah atau dihapus di sini.",
    "Tekan Pindai untuk memulai.", "Pindai drive untuk melihat petanya di sini.",                    # 203-204
    "Memindai {drive}: ...", "Memindai {drive}: {files} file, {size} sejauh ini",
    "Ditemukan {size} dalam {files} file dan {folders} folder.", "Drive terpakai: {used}.",
    "Dihentikan lebih awal, jadi hasilnya parsial.",
    "Beberapa folder dilindungi; jalankan sebagai administrator untuk menyertakannya.",
    "Jenis file", "Jenis file mana yang memakai ruang terbanyak di drive ini.",                        # 211-212
    "Pembersihan disk",
    "Hanya menghapus sisa yang aman dan dapat dibuat ulang: file sementara, cache, dan laporan crash. File Anda sendiri tidak pernah disentuh. Centang yang diinginkan, periksa ukurannya, lalu bersihkan.",
    "Periksa ukuran", "Memeriksa ukuran...", "Bersihkan yang dipilih", "Membersihkan...",              # 215-218
    "Centang setidaknya satu item dulu.", "Item yang dicentang akan membebaskan sekitar {size}.",
    "Keranjang Sampah dikosongkan secara permanen.",
    "Hapus sekitar {size} dari:\n\n{names}{note}\n\nLanjutkan?",
    "Dibebaskan {size} ({files} file). Item yang sedang dipakai dilewati.",
    "File sementara", "Ditinggalkan program di folder Temp Anda.",                                    # 224-225
    "File sementara Windows", "Folder Temp milik Windows. Jalankan sebagai admin untuk membersihkan semuanya.",
    "Cache thumbnail", "Explorer membangun ulang pratinjau gambar saat diperlukan.",
    "Dump crash dan laporan galat", "File diagnostik dari program yang crash.",
    "Cache browser", "Cache Chrome, Edge, dan Brave. Situs dimuat sedikit lebih lambat sekali.",
    "Cache shader", "Cache shader GPU. Game bisa tersendat sebentar saat dimulai berikutnya selagi ini dibangun ulang.",
    "Keranjang Sampah", "Menghapus permanen isi Keranjang Sampah.",
    "Pindahkan ke Keranjang Sampah", "folder", "file",                                                 # 238-240
    "Pindahkan {kind} ini ke Keranjang Sampah?\n\n{path}\n{size}\n\nAnda dapat memulihkannya dari Keranjang Sampah.",
    "Memindahkan ke Keranjang Sampah...",
    "Tidak dapat memindahkan ke Keranjang Sampah (sedang dipakai, dilindungi, atau dibatalkan).",
    "Memindahkan {size} ke Keranjang Sampah. Pindai lagi untuk menyegarkan jenis file.",
    "Pemindaian cepat (tabel file NTFS).",
    "Jalankan Diskuick sebagai administrator untuk pemindaian yang jauh lebih cepat.",
    "Folder", "Kosong",                                                                           # 246-247
    "mis. 1.1.1.1",
))
