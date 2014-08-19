set compare=C:\Testing\%1_Logs\nightly_compare.txt
TortoiseProc /command:update /path:"C:\%1\" /closeonend:1
TortoiseProc /command:update /path:"C:\Testing\" /closeonend:1
if "%1" == "FEBio" (
	call "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC"\vcvarsall.bat
	vcbuild C:\FEBio\FEBio.sln "Release|x64" > %compare%
) else (
  if "%1" == "FEBio2" (
		call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC"\vcvarsall.bat
		msbuild C:\FEBio2\VS2010\FEBio2.sln /p:Platform=x64 /p:Configuration="Release OpenMP" > %compare%
	)
)
C:\Testing\nightly.py %* >> %compare%
