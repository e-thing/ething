
@echo off

set ROOT_DIR=%~dp0

cd %ROOT_DIR%


call:compil "core.js" "src\core\utils.js" "src\core\deferred.js" "src\core\api.js" "src\core\arbo.js" "src\core\swagger.js"

call:compil "ui.js" "src\ui\utils.js" "src\ui\form.js" "src\ui\modal.js" "src\ui\table.js" "src\ui\browser.js" "src\ui\opendialog.js" "src\ui\savedialog.js" "src\ui\textviewer.js" "src\ui\tableviewer.js" "src\ui\mapviewer.js" "src\ui\imageviewer.js" "src\ui\graph.js" "src\ui\deviceviewer.js" "src\ui\formmodal.js"

call:compil "ui.css" "src\ui\table.css" "src\ui\browser.css" "src\ui\modal.css" "src\ui\form.css" "src\ui\common.css" "src\ui\textviewer.css" "src\ui\tableviewer.css" "src\ui\mapviewer.css" "src\ui\imageviewer.css" "src\ui\graph.css" "src\ui\deviceviewer.css"



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
