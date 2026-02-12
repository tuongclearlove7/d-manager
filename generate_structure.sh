#!/bin/bash

echo "Generating project structure..."

# =============================
# CREATE DIRECTORIES (IF NOT EXIST)
# =============================

mkdir -p backend/app/config
mkdir -p backend/app/modules
mkdir -p backend/app/websocket

# =============================
# CREATE CORE FILES (IF NOT EXIST)
# =============================

create_file_if_not_exists () {
  if [ ! -f "$1" ]; then
    touch "$1"
    echo "Created: $1"
  else
    echo "Skipped (exists): $1"
  fi
}

create_file_if_not_exists backend/app/main.py
create_file_if_not_exists backend/app/database.py
create_file_if_not_exists backend/app/listen.py
create_file_if_not_exists backend/app/config/config.py
create_file_if_not_exists backend/app/websocket/manager.py
create_file_if_not_exists deploy.sh
create_file_if_not_exists Dockerfile
create_file_if_not_exists docker-compose.yml
create_file_if_not_exists requirements.txt
create_file_if_not_exists index.html

# =============================
# WRITE create_module.sh (IF NOT EXIST)
# =============================

if [ ! -f create_module.sh ]; then
  echo "Writing create_module.sh..."

  cat <<'EOF' > create_module.sh
#!/bin/bash

BASE_DIR="backend/app/modules"

echo "Enter module name:"
read MODULE_NAME

if [ -z "$MODULE_NAME" ]; then
  echo "Module name cannot be empty!"
  exit 1
fi

MODULE_PATH="$BASE_DIR/$MODULE_NAME"

if [ -d "$MODULE_PATH" ]; then
  echo "Module already exists!"
  exit 1
fi

echo "Creating module: $MODULE_NAME"

mkdir -p "$MODULE_PATH/models"

# Create controller.py
cat <<EOT > "$MODULE_PATH/controller.py"
from fastapi import APIRouter

router = APIRouter(prefix="/$MODULE_NAME", tags=["$MODULE_NAME"])

@router.get("/")
def get_all():
    return {"message": "$MODULE_NAME controller working"}
EOT

# Capitalize first letter
CAPITALIZED="$(tr '[:lower:]' '[:upper:]' <<< ${MODULE_NAME:0:1})${MODULE_NAME:1}"

# Create service.py
cat <<EOT > "$MODULE_PATH/service.py"
class ${CAPITALIZED}Service:

    def get_all(self):
        return []
EOT

# Create model.py
cat <<EOT > "$MODULE_PATH/models/model.py"
from pydantic import BaseModel

class ${CAPITALIZED}Model(BaseModel):
    id: int
EOT

# Create dto.py
cat <<EOT > "$MODULE_PATH/models/dto.py"
from pydantic import BaseModel

class ${CAPITALIZED}DTO(BaseModel):
    id: int
EOT

echo "Module $MODULE_NAME created successfully!"
EOF

  chmod +x create_module.sh
else
  echo "Skipped (exists): create_module.sh"
fi

# =============================
# WRITE README.md (IF NOT EXIST)
# =============================

if [ ! -f README.md ]; then
  echo "Writing README.md..."

  cat <<'EOF' > README.md
# D-Manager

## 🚀 Run Project

### 1. Install dependencies

pip install -r requirements.txt

### 2. Run FastAPI

uvicorn backend.app.main:app --reload

---

## 📦 Create New Module

### Linux / Mac

chmod +x create_module.sh
./create_module.sh

### Windows (Git Bash / WSL)

bash create_module.sh

---

## 📁 Example Generated Module

If you enter:

deploy

It will generate:

backend/app/modules/deploy/
├── controller.py
├── service.py
└── models/
    ├── model.py
    └── dto.py
EOF

else
  echo "Skipped (exists): README.md"
fi

echo "Structure checked / generated successfully!"
