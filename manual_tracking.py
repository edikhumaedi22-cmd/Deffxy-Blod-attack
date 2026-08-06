import json
import csv
from datetime import datetime
from pathlib import Path

# File database sederhana menggunakan JSON
DB_FILE = Path("tracking_data.json")

# Daftar status yang tersedia
STATUSES = [
    "Pending",
    "In Progress",
    "On Hold",
    "Completed",
    "Cancelled",
    "Need Follow Up"
]

# Kolom data tracking
FIELDS = [
    "id",
    "tanggal",
    "nama_item",
    "pic",
    "status",
    "lokasi",
    "keterangan",
    "update_terakhir",
    "bukti"
]


def load_data():
    """
    Membaca data dari file JSON.
    Jika file belum ada, return list kosong.
    """
    if not DB_FILE.exists():
        return []

    try:
        with DB_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("File data JSON rusak. Membuat backup file lama.")
        backup_file = DB_FILE.with_name("tracking_data_error.json")
        DB_FILE.rename(backup_file)
        return []


def save_data(data):
    """
    Menyimpan data ke file JSON.
    """
    with DB_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_id(data):
    """
    Membuat ID tracking otomatis.
    Format: TRK-YYYYMMDD-001
    """
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"TRK-{today}-"

    numbers = []

    for item in data:
        item_id = item.get("id", "")

        if item_id.startswith(prefix):
            try:
                number = int(item_id.split("-")[-1])
                numbers.append(number)
            except ValueError:
                continue

    next_number = max(numbers, default=0) + 1

    return f"{prefix}{next_number:03d}"


def input_nonempty(prompt):
    """
    Input yang tidak boleh kosong.
    """
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Kolom ini tidak boleh kosong.")


def input_status():
    """
    Memilih status tracking.
    Bisa input nomor atau nama status.
    """
    print("\nPilih status:")

    for i, status in enumerate(STATUSES, 1):
        print(f"{i}. {status}")

    while True:
        choice = input("Masukkan nomor atau nama status: ").strip()

        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(STATUSES):
                return STATUSES[index - 1]
        else:
            for status in STATUSES:
                if choice.lower() == status.lower():
                    return status

        print("Status tidak valid. Coba lagi.")


def show_items(items):
    """
    Menampilkan daftar tracking.
    """
    if not items:
        print("\nTidak ada data tracking.")
        return

    for item in items:
        print("\n" + "=" * 60)
        print(f"ID        : {item.get('id', '-')}")
        print(f"Tanggal   : {item.get('tanggal', '-')}")
        print(f"Item      : {item.get('nama_item', '-')}")
        print(f"PIC       : {item.get('pic', '-')}")
        print(f"Status    : {item.get('status', '-')}")
        print(f"Lokasi    : {item.get('lokasi', '-')}")
        print(f"Keterangan: {item.get('keterangan', '-')}")
        print(f"Update    : {item.get('update_terakhir', '-')}")
        print(f"Bukti     : {item.get('bukti', '-')}")


def add_item(data):
    """
    Menambah data tracking baru.
    """
    print("\n--- Tambah Tracking ---")

    item = {
        "id": generate_id(data),
        "tanggal": datetime.now().strftime("%d/%m/%Y"),
        "nama_item": input_nonempty("Nama item/proses: "),
        "pic": input_nonempty("PIC: "),
        "status": input_status(),
        "lokasi": input("Lokasi (opsional, Enter jika kosong): ").strip(),
        "keterangan": input("Keterangan (opsional): ").strip(),
        "update_terakhir": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "bukti": input("Link bukti/foto (opsional): ").strip()
    }

    data.append(item)
    save_data(data)

    print(f"\nData berhasil disimpan dengan ID: {item['id']}")


def list_items(data):
    """
    Menampilkan semua data tracking.
    """
    print("\n--- Daftar Tracking ---")
    show_items(data)


def search_items(data):
    """
    Mencari data tracking berdasarkan ID, nama, PIC, status, keterangan, dsb.
    """
    print("\n--- Cari Tracking ---")

    q = input("Cari ID/nama/PIC/status/keterangan: ").strip().lower()

    if not q:
        show_items(data)
        return

    results = []

    for item in data:
        for value in item.values():
            if q in str(value).lower():
                results.append(item)
                break

    print(f"\nHasil pencarian: {len(results)} data")
    show_items(results)


def find_by_id(data, item_id):
    """
    Mencari item berdasarkan ID.
    """
    for item in data:
        if item.get("id", "").lower() == item_id.lower():
            return item

    return None


def update_item(data):
    """
    Update data tracking berdasarkan ID.
    """
    print("\n--- Update Tracking ---")

    if not data:
        print("Tidak ada data.")
        return

    item_id = input("Masukkan ID yang akan di-update: ").strip()
    item = find_by_id(data, item_id)

    if not item:
        print("ID tidak ditemukan.")
        return

    show_items([item])

    print("\nKosongkan / tekan Enter jika tidak ingin mengubah.")

    nama = input(f"Nama item [{item.get('nama_item', '')}]: ").strip()
    if nama:
        item["nama_item"] = nama

    pic = input(f"PIC [{item.get('pic', '')}]: ").strip()
    if pic:
        item["pic"] = pic

    change_status = input("Ubah status? (y/n): ").strip().lower()
    if change_status == "y":
        item["status"] = input_status()

    lokasi = input(f"Lokasi [{item.get('lokasi', '')}]: ").strip()
    if lokasi:
        item["lokasi"] = lokasi

    keterangan = input(f"Keterangan [{item.get('keterangan', '')}]: ").strip()
    if keterangan:
        item["keterangan"] = keterangan

    bukti = input(f"Bukti [{item.get('bukti', '')}]: ").strip()
    if bukti:
        item["bukti"] = bukti

    item["update_terakhir"] = datetime.now().strftime("%d/%m/%Y %H:%M")

    save_data(data)

    print("\nData berhasil di-update.")
    show_items([item])


def delete_item(data):
    """
    Menghapus data tracking berdasarkan ID.
    """
    print("\n--- Hapus Tracking ---")

    if not data:
        print("Tidak ada data.")
        return

    item_id = input("Masukkan ID yang akan dihapus: ").strip()
    item = find_by_id(data, item_id)

    if not item:
        print("ID tidak ditemukan.")
        return

    show_items([item])

    confirm = input("Yakin hapus data ini? (y/n): ").strip().lower()

    if confirm == "y":
        data.remove(item)
        save_data(data)
        print("Data berhasil dihapus.")
    else:
        print("Hapus dibatalkan.")


def export_csv(data):
    """
    Export data tracking ke file CSV.
    """
    print("\n--- Export CSV ---")

    if not data:
        print("Tidak ada data untuk export.")
        return

    filename = input("Nama file CSV [tracking_export.csv]: ").strip()

    if not filename:
        filename = "tracking_export.csv"

    if not filename.lower().endswith(".csv"):
        filename += ".csv"

    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()

            for item in data:
                writer.writerow({
                    field: item.get(field, "")
                    for field in FIELDS
                })

        print(f"Export berhasil: {filename}")

    except Exception as e:
        print(f"Gagal export CSV: {e}")


def print_menu():
    """
    Menampilkan menu utama.
    """
    print("\n" + "=" * 40)
    print("MANUAL TRACKING - PYTHON CLI")
    print("=" * 40)
    print("1. Tambah tracking")
    print("2. Lihat semua tracking")
    print("3. Cari tracking")
    print("4. Update tracking")
    print("5. Hapus tracking")
    print("6. Export ke CSV")
    print("0. Keluar")


def main():
    """
    Fungsi utama program.
    """
    data = load_data()

    while True:
        print_menu()

        choice = input("Pilih menu: ").strip()

        if choice == "1":
            add_item(data)

        elif choice == "2":
            list_items(data)

        elif choice == "3":
            search_items(data)

        elif choice == "4":
            update_item(data)

        elif choice == "5":
            delete_item(data)

        elif choice == "6":
            export_csv(data)

        elif choice == "0":
            save_data(data)
            print("Program selesai.")
            print("Data tersimpan di:", DB_FILE.resolve())
            break

        else:
            print("Menu tidak dikenal. Silakan pilih lagi.")


if __name__ == "__main__":
    main()
