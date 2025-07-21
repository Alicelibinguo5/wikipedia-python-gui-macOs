# Wikipedia Search GUI

A simple Python desktop application for searching Wikipedia articles using PyQt6.

## Features

- Clean, modern GUI interface
- Real-time Wikipedia article search
- Configurable result limits (5-20 articles)
- Direct article links that open in browser
- Cross-platform compatibility

## Getting Started

### Prerequisites

- Python 3.7+
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd simple-python-gui
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
python src/app.py
```

### Building Executable

To create a standalone application:

```bash
# Install PyInstaller (included in requirements.txt)
python -m PyInstaller WikiSearch.spec

# The executable will be in the dist/ folder
```

### Creating macOS DMG (macOS only)

```bash
# Install create-dmg
brew install create-dmg

# Run the build script
./build.sh
```

## Usage

1. Launch the application
2. Enter your search term in the text field
3. Select number of results (5-20)
4. Click "Search" or press Enter
5. Click "Open" links to view articles in your browser

## Project Structure

- `src/app.py` - Main application code
- `examples/` - Sample GUI implementations
- `requirements.txt` - Python dependencies
- `WikiSearch.spec` - PyInstaller configuration