@echo off
setlocal EnableDelayedExpansion

REM Luôn chạy từ thư mục chứa script
cd /d "%~dp0"

echo =====================================
echo Generating / Checking Project Structure
echo =====================================

REM =============================
REM CREATE DIRECTORIES
REM =============================

call :createDir backend
call :createDir backend\app
call :createDir backend\app\config
call :createDir backend\app\modules
call :createDir backend\app\websocket

REM =============================
REM CREATE CORE FILES
REM =============================

call :createFile backend\app\main.py
call :createFile backend\app\database.py
call :createFile backend\app\listen.py
call :createFile backend\app\config\config.py
call :createFile backend\app\websocket\manager.py
call :createFile deploy.sh
call :createFile Dockerfile
call :createFile docker-compose.yml
call :createFile requirements.txt
call :createFile index.html

REM =============================
REM CREATE create_module.bat
REM =============================

if not exist "create_module.bat" (
    echo Creating create_module.bat...
    (
        echo @echo off
        echo setlocal
        echo cd /d "%%~dp0"
        echo.
        echo set BASE_DIR=backend\app\modules
        echo.
        echo if not exist "%%BASE_DIR%%" (
        echo     echo Modules directory not found!
        echo     echo Please run generate_structure.bat first.
        echo     pause
        echo     exit /b 1
        echo )
        echo.
        echo set /p MODULE_NAME=Enter module name:
        echo.
        echo if "%%MODULE_NAME%%"=="" (
        echo     echo Module name cannot be empty!
        echo     pause
        echo     exit /b 1
        echo )
        echo.
        echo set MODULE_PATH=%%BASE_DIR%%\%%MODULE_NAME%%
        echo.
        echo if exist "%%MODULE_PATH%%" (
        echo     echo Module already exists!
        echo     pause
        echo     exit /b 1
        echo )
        echo.
        echo echo Creating module: %%MODULE_NAME%%
        echo mkdir "%%MODULE_PATH%%" ^|^| (
        echo     echo Failed to create module directory!
        echo     pause
        echo     exit /b 1
        echo )
        echo mkdir "%%MODULE_PATH%%\models"
        echo.
        echo type nul ^> "%%MODULE_PATH%%\controller.py"
        echo type nul ^> "%%MODULE_PATH%%\service.py"
        echo type nul ^> "%%MODULE_PATH%%\models\model.py"
        echo type nul ^> "%%MODULE_PATH%%\models\dto.py"
        echo.
        echo echo Module %%MODULE_NAME%% created successfully!
        echo pause
    ) > create_module.bat

    echo create_module.bat created successfully.
) else (
    echo Skipped create_module.bat (already exists)
)

REM =============================
REM CREATE create_module.sh
REM =============================

if not exist "create_module.sh" (
    echo Creating create_module.sh...
    (
        echo #!/bin/bash
        echo.
        echo cd "$$(dirname "$$0")"
        echo.
        echo BASE_DIR="backend/app/modules"
        echo.
        echo if [ ! -d "$$BASE_DIR" ]; then
        echo     echo "Modules directory not found!"
        echo     echo "Please run generate_structure.sh first."
        echo     exit 1
        echo fi
        echo.
        echo read -p "Enter module name: " MODULE_NAME
        echo.
        echo if [ -z "$$MODULE_NAME" ]; then
        echo     echo "Module name cannot be empty!"
        echo     exit 1
        echo fi
        echo.
        echo MODULE_PATH="$$BASE_DIR/$$MODULE_NAME"
        echo.
        echo if [ -d "$$MODULE_PATH" ]; then
        echo     echo "Module already exists!"
        echo     exit 1
        echo fi
        echo.
        echo echo "Creating module: $$MODULE_NAME"
        echo mkdir -p "$$MODULE_PATH/models"
        echo.
        echo touch "$$MODULE_PATH/controller.py"
        echo touch "$$MODULE_PATH/service.py"
        echo touch "$$MODULE_PATH/models/model.py"
        echo touch "$$MODULE_PATH/models/dto.py"
        echo.
        echo echo "Module $$MODULE_NAME created successfully!"
    ) > create_module.sh

    echo create_module.sh created successfully.
) else (
    echo Skipped create_module.sh (already exists)
)

REM =============================
REM CREATE README.md (nếu chưa tồn tại)
REM =============================

if not exist "README.md" (
    echo Creating README.md...

    (
        echo # D-Manager
        echo.
        echo ## Run Project
        echo.
        echo Install dependencies:
        echo pip install -r requirements.txt
        echo.
        echo Run FastAPI:
        echo uvicorn backend.app.main:app --reload
        echo.
        echo.
        echo ## Create New Module
        echo.
        echo Linux:
        echo chmod +x create_module.sh
        echo ./create_module.sh
        echo.
        echo Windows ^(Git Bash^):
        echo bash create_module.sh
        echo.
        echo Example module structure:
        echo backend/app/modules/deploy/
        echo ├── controller.py
        echo ├── service.py
        echo └── models/
        echo     ├── model.py
        echo     └── dto.py
    ) > README.md

    echo README.md created successfully.
) else (
    echo Skipped README.md (already exists)
)

echo.
echo =====================================
echo Structure check completed!
echo =====================================
pause
exit /b 0


REM =============================
REM FUNCTIONS
REM =============================

:createDir
if not exist "%~1" (
    mkdir "%~1"
    echo Created directory: %~1
) else (
    echo Skipped directory: %~1
)
exit /b

:createFile
if not exist "%~1" (
    type nul > "%~1"
    echo Created file: %~1
) else (
    echo Skipped file: %~1
)
exit /b