@echo off
setlocal
cd /d "%~dp0"

set BASE_DIR=backend\app\modules

if not exist "%BASE_DIR%" (
    echo Modules directory not found!
    echo Please run generate_structure.bat first.
    pause
    exit /b 1
)

set /p MODULE_NAME=Enter module name:

if "%MODULE_NAME%"=="" (
    echo Module name cannot be empty!
    pause
    exit /b 1
)

set MODULE_PATH=%BASE_DIR%\%MODULE_NAME%

if exist "%MODULE_PATH%" (
    echo Module already exists!
    pause
    exit /b 1
)

echo Creating module: %MODULE_NAME%
mkdir "%MODULE_PATH%" || (
    echo Failed to create module directory!
    pause
    exit /b 1
)
mkdir "%MODULE_PATH%\models"

type nul > "%MODULE_PATH%\controller.py"
type nul > "%MODULE_PATH%\service.py"
type nul > "%MODULE_PATH%\models\model.py"
type nul > "%MODULE_PATH%\models\dto.py"

echo Module %MODULE_NAME% created successfully!
pause
