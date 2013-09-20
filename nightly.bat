set compare=C:\Testing\%1_Logs\nightly_compare.txt
TortoiseProc /command:update /path:"C:\%1\" /closeonend:1
TortoiseProc /command:update /path:"C:\Testing\" /closeonend:1
REM if %COMPUTERNAME%==CIBC-RD7 (
	call "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC"\vcvarsall.bat
	vcbuild C:\FEBio\FEBio.sln "Release|x64" > %compare%
REM ) else (
REM 	if "%1" == "FEBio" (
REM 		call "C:\Program Files\Microsoft Visual Studio 9.0\VC"\vcvarsall.bat
REM 		vcbuild C:\FEBio\FEBio.sln "Release|Win32" > %compare%
REM 	) else (
REM 		call "C:\Program Files\Microsoft Visual Studio 10.0\VC"\vcvarsall.bat
REM 		msbuild C:\FEBio2\VS2010\FEBio2.sln /p:Platform=Win32 /p:Configuration=Release > %compare%
REM 	)
REM )
C:\Testing\nightly.py %* >> %compare%
