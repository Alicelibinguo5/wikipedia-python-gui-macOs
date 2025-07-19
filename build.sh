#!/bin/bash
pyinstaller --name="WikiSearch" \
            --windowed \
            --onefile \
            --add-data "src:src" \
            --icon="src/icon.icns" \
            src/app.py