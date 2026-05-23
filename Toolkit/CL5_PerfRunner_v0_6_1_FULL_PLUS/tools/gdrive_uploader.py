# Requires: pip install pydrive2 ; needs client_secrets.json (OAuth Desktop) in working dir
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pathlib import Path
def upload_files(folder_id: str, paths):
    gauth=GoogleAuth(); gauth.LocalWebserverAuth()
    drive=GoogleDrive(gauth); out=[]
    for p in paths:
        p=Path(p); f=drive.CreateFile({'parents':[{'id':folder_id}], 'title':p.name})
        f.SetContentFile(str(p)); f.Upload(); out.append({'name':p.name,'id':f['id']})
    return out
