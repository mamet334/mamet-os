import sys
import os
from pathlib import Path

# Tambahkan path agar modul mamet-os bisa diimport
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from memory.google_drive_sync import GoogleDriveSync

def check_backups():
    print("="*60)
    print("MEMERIKSA ISI FOLDER GOOGLE DRIVE 'MametOS_Backups'")
    print("="*60)
    
    sync = GoogleDriveSync("default@mamet.os")
    service = sync.get_service()
    
    # Dapatkan ID folder
    folder_id = sync._get_or_create_folder("MametOS_Backups")
    print(f"✅ Folder Ditemukan! (ID: {folder_id})")
    
    # Ambil daftar file di dalam folder tersebut
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name, modifiedTime, size)').execute()
    items = results.get('files', [])
    
    if not items:
        print("❌ Folder kosong. Tidak ada file backup yang ditemukan.")
    else:
        print(f"\n📂 Terdapat {len(items)} file di dalam folder:")
        for item in items:
            size_kb = int(item.get('size', 0)) / 1024
            print(f"  - 📄 {item['name']}")
            print(f"       Ukuran : {size_kb:.2f} KB")
            print(f"       Diubah : {item.get('modifiedTime')}")
            
    print("="*60)

if __name__ == "__main__":
    check_backups()
