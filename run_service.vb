' start-app.vbs
' Skrip untuk menjalankan 3 service sekaligus (Bun API, Vue Frontend, ML Service)
' Letakkan file ini di root folder project (sejajar dengan folder api, vue, ml)

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Dapatkan folder di mana skrip ini berada (Root Project)
CurrentDirectory = FSO.GetParentFolderName(WScript.ScriptFullName)

' --- SERVICE 1: BUN API ---
' Masuk ke folder "api" dan jalankan "bun run dev"
' Parameter 1 artinya jendela cmd akan terlihat (Normal Focus)
WshShell.Run "cmd /k ""cd /d """ & CurrentDirectory & "\api"" && bun run dev""", 1, False

' --- SERVICE 2: VUE FRONTEND ---
' Masuk ke folder "vue" dan jalankan "npm run dev"
WshShell.Run "cmd /k ""cd /d """ & CurrentDirectory & "\vue"" && npm run dev""", 1, False

' --- SERVICE 3: ML SERVICE ---
' Masuk ke root folder, aktifkan virtual environment (jika ada), lalu jalankan uvicorn
' Asumsi: venv ada di dalam folder ml\.venv (standar python venv di windows)

Dim PythonCmd
PythonCmd = "python" ' Default fallback ke python global

' Cek apakah ada virtual environment di ml/.venv/Scripts/python.exe
If FSO.FileExists(CurrentDirectory & "\ml\.venv\Scripts\python.exe") Then
    PythonCmd = CurrentDirectory & "\ml\.venv\Scripts\python.exe"
End If

' Jalankan perintah uvicorn dari root directory
' Kita set PYTHONPATH ke root agar modul "ml.index" terbaca
' Kita tambahkan --env-file untuk memuat variabel dari ml/.env
WshShell.Run "cmd /k ""cd /d """ & CurrentDirectory & """ && set PYTHONPATH=. && " & PythonCmd & " -m uvicorn ml.index:app --host 0.0.0.0 --port 3102 --reload --env-file ml/.env""", 1, False
