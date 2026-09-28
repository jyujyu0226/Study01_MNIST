$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1) Find python (py launcher first, then python)
$exe = $null
foreach ($c in @('py', 'python')) {
    if (Get-Command $c -ErrorAction SilentlyContinue) {
        try {
            $p = (& $c -c "import sys;print(sys.executable)" 2>$null | Select-Object -First 1)
            if ($p -and (Test-Path $p)) { $exe = $p; break }
        } catch {}
    }
}
if (-not $exe) { throw 'Python not found. Install Python 3.12 from https://www.python.org/downloads/ (check "Add python.exe to PATH").' }
$pyw = Join-Path (Split-Path $exe) 'pythonw.exe'
if (-not (Test-Path $pyw)) { throw "pythonw.exe not found next to $exe" }
Write-Host "Using Python: $exe"

# 2) Install libraries and pre-train the model once (this window shows progress)
& $exe -m pip install numpy pillow tensorflow
if ($LASTEXITCODE -ne 0) { throw 'pip install failed. If TensorFlow failed, use Python 3.12.' }
& $exe (Join-Path $here 'app.py') --prepare
if ($LASTEXITCODE -ne 0) { throw 'Model preparation failed.' }

# 3) Create desktop shortcut: pythonw = no black console window
$name = 'MNIST ' + [regex]::Unescape('\uC190\uAE00\uC528 \uC778\uC2DD')
$desktop = [Environment]::GetFolderPath('Desktop')
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut((Join-Path $desktop "$name.lnk"))
$lnk.TargetPath = $pyw
$lnk.Arguments = '"' + (Join-Path $here 'app.py') + '"'
$lnk.WorkingDirectory = $here
$lnk.IconLocation = (Join-Path $here 'icon.ico') + ',0'
$lnk.Description = 'MNIST digit recognizer'
$lnk.Save()
Write-Host "Done! Shortcut created on Desktop: $name"
