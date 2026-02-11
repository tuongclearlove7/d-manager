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

touch "$MODULE_PATH/controller.py"
touch "$MODULE_PATH/service.py"
touch "$MODULE_PATH/models/model.py"
touch "$MODULE_PATH/models/dto.py"

echo "Module $MODULE_NAME created successfully!"
