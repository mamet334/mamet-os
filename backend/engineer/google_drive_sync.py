import os
import socket
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveSync:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user_dir = Path(os.path.expanduser("~")) / ".mamet" / user_id
        self.user_dir.mkdir(parents=True, exist_ok=True)
        self.token_path = self.user_dir / "token.json"
        self.sync_log_path = self.user_dir / "sync.log"
        self.creds = None

    def _get_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    def authenticate(self):
        """F2: Mengautentikasi pengguna dan mendapatkan token.json"""
        # Sesuaikan dengan lokasi sebenarnya credentials.json
        cred_path = Path(os.path.join(os.getcwd(), "backend", "credentials.json"))
        if not cred_path.exists():
            cred_path = Path(os.path.join(os.getcwd(), "credentials.json"))
            if not cred_path.exists():
                raise FileNotFoundError("credentials.json tidak ditemukan!")
            
        if self.token_path.exists():
            self.creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                port = self._get_free_port()
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(cred_path), SCOPES)
                self.creds = flow.run_local_server(port=port)
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())
                
        return {"status": "success", "message": "Warisan Digital aktif. MAMET OS tersambung ke Google Drive."}
        
    def _get_service(self):
        if not self.creds:
            if self.token_path.exists():
                self.creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            else:
                raise Exception("Belum login. Gunakan fitur Legacy Wizard.")
        return build('drive', 'v3', credentials=self.creds)

    def sync_to_cloud(self, backup_zip_path: str):
        """F1: Sinkronisasi ke Google Drive"""
        if not self.token_path.exists():
            return False # Belum diaktifkan, abaikan
            
        try:
            service = self._get_service()
            file_metadata = {'name': os.path.basename(backup_zip_path)}
            media = MediaFileUpload(backup_zip_path, mimetype='application/zip')
            
            file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
                                        
            msg = f"{datetime.now().isoformat()} - SUCCESS - {os.path.basename(backup_zip_path)}\n"
            with open(self.sync_log_path, 'a') as f:
                f.write(msg)
            return True
        except Exception as e:
            msg = f"{datetime.now().isoformat()} - FAILED - {str(e)}\n"
            with open(self.sync_log_path, 'a') as f:
                f.write(msg)
            return False
            
    def get_sync_status(self):
        """F1: Mengambil status sinkronisasi terakhir"""
        if not self.token_path.exists():
            return {"status": "unconfigured", "message": "Warisan Digital belum diaktifkan"}
            
        if not self.sync_log_path.exists():
            return {"status": "pending", "message": "Belum ada sinkronisasi"}
            
        try:
            with open(self.sync_log_path, 'r') as f:
                lines = f.readlines()
                if not lines:
                    return {"status": "pending", "message": "Belum ada sinkronisasi"}
                
                last_line = lines[-1].strip()
                if "SUCCESS" in last_line:
                    time_str = last_line.split(" - ")[0]
                    return {"status": "success", "time": time_str, "message": "Berhasil"}
                else:
                    return {"status": "failed", "message": "Sinkron gagal"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
