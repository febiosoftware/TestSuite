call "C:\Program Files\Microsoft Visual Studio 9.0\VC"\vcvarsall.bat
TortoiseProc /command:update /path:"C:\%1\" /closeonend:1
TortoiseProc /command:update /path:"C:\Testing\" /closeonend:1
if "%1" == "FEBio" vcbuild C:\FEBio\FEBio.sln "Release|Win32"
if "%1" == "FEBio2" vcbuild C:\FEBio2\VS2008\FEBio2.sln "Release|Win32"

