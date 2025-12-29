
#!/bin/bash

# Universal Website Scraper - Run Script

set -e

echo "🚀 Starting Universal Website Scraper setup..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.10+ required. Found: $python_version"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Start server
echo "✅ Setup complete!"
echo "🌍 Starting server on http://localhost:8000"
echo ""
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

