#!/bin/bash
# Quick setup script for OpenIssue

echo "Setting up OpenIssue..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Edit .env with your GitHub OAuth credentials"
fi

# Backend setup
cd backend
if [ ! -d .venv ]; then
    echo "Creating Python virtual environment..."
    python -m venv .venv
fi

echo "Installing backend dependencies..."
.venv/bin/pip install -r requirements.txt

cd ..

# CLI setup
cd cli
echo "Installing CLI tool..."
pip install -e .

cd ..

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your GitHub OAuth credentials"
echo "2. Start backend: cd backend && .venv/bin/python run.py"
echo "3. Start frontend: cd frontend && python -m http.server 3000"
echo "4. Visit: http://localhost:3000"
