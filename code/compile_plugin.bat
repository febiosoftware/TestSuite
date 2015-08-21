set compile=C:\Testing\Logs\FEBio2_Logs\plugin_%2.txt
call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC"\vcvarsall.bat
msbuild C:\Software\Plugins\%1\VS2010\%1.sln /p:Platform=x64 /p:Configuration="Release" >> %compile%