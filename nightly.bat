set compare=C:\Testing\%1_Logs\nightly_compare.txt
TortoiseProc /command:update /path:"C:\%1\" /closeonend:1
TortoiseProc /command:update /path:"C:\Testing\" /closeonend:1
if %COMPUTERNAME%==CIBC-RD7 (
	call "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC"\vcvarsall.bat
	vcbuild C:\FEBio\FEBio.sln "Release|x64" > %compare%
) else (
	call "C:\Program Files\Microsoft Visual Studio 9.0\VC"\vcvarsall.bat
	if "%1" == "FEBio" vcbuild C:\FEBio\FEBio.sln "Release|Win32" > %compare%
	if "%1" == "FEBio2" vcbuild C:\FEBio2\VS2008\FEBio2.sln "Release|Win32" > %compare%
)
C:\Testing\nightly.py %* >> %compare%
