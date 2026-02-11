#!/bin/bash

echo "Generating project structure..."

# =============================
# CREATE DIRECTORIES
# =============================

mkdir -p backend/app/config
mkdir -p backend/app/modules
mkdir -p backend/app/websocket

# =============================
# CREATE CORE FILES
# =============================

touch backend/app/main.py
touch backend/app/database.py
touch backend/app/listen.py
touch backend/app/config/config.py
touch backend/app/websocket/manager.py
touch deploy.sh
touch Dockerfile
touch docker-compose.yml
touch requirements.txt
touch index.html

# =============================
# WRITE create_module.sh
# =============================

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

# Create service.py
cat <<EOT > "$MODULE_PATH/service.py"
class ${MODULE_NAME^}Service:

    def get_all(self):
        return []
EOT

# Create model.py
cat <<EOT > "$MODULE_PATH/models/model.py"
from pydantic import BaseModel

class ${MODULE_NAME^}Model(BaseModel):
    id: int
EOT

# Create dto.py
cat <<EOT > "$MODULE_PATH/models/dto.py"
from pydantic import BaseModel

class ${MODULE_NAME^}DTO(BaseModel):
    id: int
EOT

echo "Module $MODULE_NAME created successfully!"
EOF

chmod +x create_module.sh

# =============================
# WRITE README.md
# =============================

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

echo "Structure generated successfully!"
