import os
import io
import json
import shutil
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Scope yang dibutuhkan untuk membaca dan menulis file di Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveSync:
    """Modul untuk menyinkronkan memori pengguna (SQLite & ChromaDB) ke Google Drive."""
    
    def __init__(self, user_email: str):
        self.user_email = user_email
        self.creds = None
        
        # Path folder data pengguna
        self.base_dir = Path(os.path.expanduser("~")) / ".mamet" / user_email
        self.token_path = self.base_dir / "token.json"
        
        # Asumsi credentials.json ditaruh di root backend
        self.credentials_path = Path(__file__).parent.parent / "credentials.json"
        self.drive_folder_id = None
        
    def authenticate(self) -> bool:
        """Autentikasi ke Google Drive menggunakan OAuth."""
        if not self.credentials_path.exists():
            print(f"❌ File credentials.json tidak ditemukan di {self.credentials_path}")
            return False
            
        if self.token_path.exists():
            self.creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            
        # Jika tidak ada token valid, minta pengguna login
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), SCOPES)
                self.creds = flow.run_local_server(port=0)
                
            # Simpan kredensial untuk kali berikutnya
            self.base_dir.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())
                
        return True
        
    def get_service(self):
        """Mendapatkan instance layanan Google Drive."""
        if not self.creds:
            if not self.authenticate():
                raise Exception("Gagal autentikasi Google Drive. Pastikan credentials.json tersedia.")
        return build('drive', 'v3', credentials=self.creds)

    def _get_or_create_folder(self, folder_name: str) -> str:
        """Mencari folder di Drive, jika tidak ada, buat baru."""
        service = self.get_service()
        
        # Cari folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        
        if items:
            return items[0]['id']
            
        # Jika tidak ada, buat folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

    def backup_database(self) -> dict:
        """Mengunggah memory.db ke Google Drive."""
        try:
            db_path = self.base_dir / "memory.db"
            if not db_path.exists():
                return {"status": "error", "message": f"Database {db_path} tidak ditemukan."}

            service = self.get_service()
            folder_id = self._get_or_create_folder("MametOS_Backups")
            
            # Cari file lama untuk ditimpa (update), bukan membuat duplikat
            query = f"name='memory_{self.user_email}.db' and '{folder_id}' in parents and trashed=false"
            results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
            items = results.get('files', [])
            
            media = MediaFileUpload(str(db_path), mimetype='application/x-sqlite3', resumable=True)
            
            if items:
                # Update file yang sudah ada
                file_id = items[0]['id']
                service.files().update(fileId=file_id, media_body=media).execute()
                msg = "✅ Backup database berhasil (Diperbarui)."
            else:
                # Buat file baru
                file_metadata = {
                    'name': f'memory_{self.user_email}.db',
                    'parents': [folder_id]
                }
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                msg = "✅ Backup database berhasil (File Baru)."
                
            return {"status": "success", "message": msg}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def restore_database(self) -> dict:
        """Mengunduh memory.db dari Google Drive dan menimpa file lokal."""
        try:
            service = self.get_service()
            folder_id = self._get_or_create_folder("MametOS_Backups")
            
            query = f"name='memory_{self.user_email}.db' and '{folder_id}' in parents and trashed=false"
            results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
            items = results.get('files', [])
            
            if not items:
                return {"status": "error", "message": "Tidak ada backup yang ditemukan di Google Drive."}
                
            file_id = items[0]['id']
            request = service.files().get_media(fileId=file_id)
            
            db_path = self.base_dir / "memory.db"
            fh = io.FileIO(str(db_path), 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                
            return {"status": "success", "message": "✅ Pemulihan (Restore) database berhasil!"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def backup_chromadb(self) -> dict:
        """Mengompres folder chroma_db menjadi ZIP dan mengunggahnya ke Drive."""
        try:
            # Asumsi chroma_db ada di folder backend/
            chroma_path = Path(__file__).parent.parent / "chroma_db"
            if not chroma_path.exists():
                return {"status": "error", "message": f"Folder ChromaDB tidak ditemukan di {chroma_path}."}
                
            zip_filename = f"chromadb_{self.user_email}"
            zip_filepath = self.base_dir / f"{zip_filename}.zip"
            
            # Kompres folder menjadi zip
            shutil.make_archive(str(self.base_dir / zip_filename), 'zip', str(chroma_path))
            
            service = self.get_service()
            folder_id = self._get_or_create_folder("MametOS_Backups")
            
            # Cari file lama untuk ditimpa
            query = f"name='{zip_filename}.zip' and '{folder_id}' in parents and trashed=false"
            results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
            items = results.get('files', [])
            
            media = MediaFileUpload(str(zip_filepath), mimetype='application/zip', resumable=True)
            
            if items:
                file_id = items[0]['id']
                service.files().update(fileId=file_id, media_body=media).execute()
                msg = "✅ Backup ChromaDB (RAG) berhasil (Diperbarui)."
            else:
                file_metadata = {
                    'name': f'{zip_filename}.zip',
                    'parents': [folder_id]
                }
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                msg = "✅ Backup ChromaDB (RAG) berhasil (File Baru)."
                
            # Hapus file zip lokal untuk menghemat tempat
            if zip_filepath.exists():
                try:
                    os.remove(zip_filepath)
                except OSError:
                    pass
                
            return {"status": "success", "message": msg}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Test script jika dijalankan secara standalone
    print("MENGUJI MODUL GOOGLE DRIVE SYNC...")
    sync = GoogleDriveSync("default@mamet.os")
    
    if not sync.credentials_path.exists():
        print("TIDAK ADA credentials.json. Harap masukkan file credentials.json dari Google Cloud Console ke folder backend/.")
    else:
        print("Melakukan backup memory.db...")
        res = sync.backup_database()
        print(res['message'])
        
        print("Melakukan backup chroma_db...")
        res_chroma = sync.backup_chromadb()
        print(res_chroma['message'])
