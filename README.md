# D-Manager

## Run Project

Install dependencies:
    pip install -r requirements.txt

Run FastAPI:
    uvicorn backend.app.main:app --reload


## Create New Module

Linux:
    chmod +x create_module.sh
    ./create_module.sh

Windows:
    create_module.bat

Example module structure:
    backend/app/modules/deploy/
        controller.py
        service.py
        models/
            model.py
            dto.py
