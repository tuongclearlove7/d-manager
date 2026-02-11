@echo off
echo Generating project structure...

REM =============================
REM CREATE DIRECTORIES
REM =============================

mkdir backend\app\config 2>nul
mkdir backend\app\modules 2>nul
mkdir backend\app\websocket 2>nul

REM =============================
REM CREATE EMPTY CORE FILES
REM =============================

type nul > backend\app\main.py
type nul > backend\app\database.py
type nul > backend\app\listen.py
type nul > backend\app\config\config.py
type nul > backend\app\websocket\manager.py
type nul > deploy.sh
type nul > Dockerfile
type nul > docker-compose.yml
type nul > requirements.txt
type nul > index.html

REM =============================
REM WRITE create_module.sh
REM =============================

echo Writing create_module.sh...

(
echo #!/bin/bash
echo.
echo BASE_DIR="backend/app/modules"
echo.
echo echo "Enter module name:"
echo read MODULE_NAME
echo.
echo if [ -z "$MODULE_NAME" ]; then
echo   echo "Module name cannot be empty!"
echo   exit 1
echo fi
echo.
echo MODULE_PATH="$BASE_DIR/$MODULE_NAME"
echo.
echo if [ -d "$MODULE_PATH" ]; then
echo   echo "Module already exists!"
echo   exit 1
echo fi
echo.
echo echo "Creating module: $MODULE_NAME"
echo mkdir -p "$MODULE_PATH/models"
echo.
echo touch "$MODULE_PATH/controller.py"
echo touch "$MODULE_PATH/service.py"
echo touch "$MODULE_PATH/models/model.py"
echo touch "$MODULE_PATH/models/dto.py"
echo.
echo echo "Module $MODULE_NAME created successfully!"
) > create_module.sh

REM =============================
REM WRITE README.md
REM =============================

echo Writing README.md...

(
echo # D-Manager
echo.
echo ## Run Project
echo.
echo Install dependencies:
echo     pip install -r requirements.txt
echo.
echo Run FastAPI:
echo     uvicorn backend.app.main:app --reload
echo.
echo.
echo ## Create New Module
echo.
echo Linux:
echo     chmod +x create_module.sh
echo     ./create_module.sh
echo.
echo Windows (Git Bash):
echo     bash create_module.sh
echo.
echo Example module structure:
echo     backend/app/modules/deploy/
echo         controller.py
echo         service.py
echo         models/
echo             model.py
echo             dto.py
) > README.md

echo.
echo Structure generated successfully!
pause
