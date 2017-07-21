
@echo off

set ROOT_DIR=%~dp0

cd %ROOT_DIR%


call:compil "core.js" "src\utils.js" "src\node.js" "src\event.js" "src\deferred.js" "src\api.js" "src\arbo.js" "src\rules.js"




pause


::--------------------------------------------------------
::-- Function section starts below here
::--------------------------------------------------------

:compil

set out=%~1
shift

echo compiling %out% ...

echo. 2>%out%

:loop

set file=%~1
echo adding %file% ...

echo. >> %out%
echo /* @file: %file% */ >> %out%
type %file% >> %out%

shift
if not "%~1"=="" goto loop


rem minify
rem 
rem echo minifying %out% ...
rem 
rem FOR %%i IN ("%out%") DO (
rem 	copy %%i %%~ni.min%%~xi > NUL
rem )


goto:eof
