@echo off
setlocal

REM ============================================================
REM run_test.bat - inline-expand end-to-end test
REM
REM Usage: Edit CTAGS path below if ctags is not in system PATH,
REM        then double-click or run from cmd.
REM ============================================================

set GBFILE=%~dp0ProcessTaskForGB_test.cpp
set TASKFILE=%~dp0ProcessTask_test.cpp
set TMPDIR=%~dp0tmp
set SCRIPTS=%~dp0..\scripts
set CTAGS=ctags.exe
set OUTFILE=%TMPDIR%\ProcessTask_inlined.cpp

REM If ctags is not in PATH, uncomment and set full path:
REM set CTAGS=D:\MyProject\tools\ctags.exe

echo [Step 1] mkdir TMPDIR
mkdir "%TMPDIR%" 2>nul

echo [Step 2] ctags extraction
"%CTAGS%" --output-format=json --fields=+neS --kinds-C++=f --language-force=C++ -f "%TMPDIR%\ctags_output.json" "%GBFILE%"
if errorlevel 1 (echo FAILED step2 && exit /b 1)

echo [Step 3] Extract function bodies
type "%GBFILE%" | python "%SCRIPTS%\step1_extract_bodies.py" "%TMPDIR%\ctags_output.json" "%TMPDIR%\gb_functions.json"
if errorlevel 1 (echo FAILED step3 && exit /b 1)

echo [Step 4] Find call sites
type "%TASKFILE%" | python "%SCRIPTS%\step2_find_calls.py" "%TMPDIR%\gb_functions.json" "%TMPDIR%\call_sites.json"
if errorlevel 1 (echo FAILED step4 && exit /b 1)

echo [Step 5] Inline expand
type "%TASKFILE%" | python "%SCRIPTS%\step3_inline_expand.py" "%TMPDIR%\gb_functions.json" "%TMPDIR%\call_sites.json" > "%OUTFILE%"
if errorlevel 1 (echo FAILED step5 && exit /b 1)

echo.
echo === DONE === Output: %OUTFILE%
endlocal

pause
