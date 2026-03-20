#!/bin/bash

echo "🔍 Verifying AI Privacy Amanuensis Setup"
echo "========================================"
echo ""

PROJECT_DIR="/Users/y4l1/Documents/GDGJP-Hackathon/ai-privacy-amanuensis"
BACKEND_DIR="$PROJECT_DIR/backend"

# Check Node.js
echo "✓ Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "  Node.js: $NODE_VERSION"
else
    echo "  ❌ Node.js not found!"
    exit 1
fi

# Check npm
echo "✓ Checking npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "  npm: $NPM_VERSION"
else
    echo "  ❌ npm not found!"
    exit 1
fi

# Check Python
echo "✓ Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  $PYTHON_VERSION"
else
    echo "  ❌ Python not found!"
    exit 1
fi

# Check uv
echo "✓ Checking uv..."
if command -v uv &> /dev/null; then
    echo "  uv: installed"
else
    echo "  ❌ uv not found!"
    exit 1
fi

# Check frontend dependencies
echo ""
echo "✓ Checking Frontend Dependencies..."
cd "$PROJECT_DIR"
MISSING_FRONTEND=0
for pkg in next react typescript; do
    if npm list $pkg &>/dev/null 2>&1; then
        VERSION=$(npm list $pkg 2>/dev/null | grep " $pkg@" | awk '{print $NF}')
        echo "  ✓ $pkg: $VERSION"
    else
        echo "  ❌ $pkg: MISSING"
        MISSING_FRONTEND=1
    fi
done

# Check backend dependencies
echo ""
echo "✓ Checking Backend Python Packages..."
cd "$BACKEND_DIR"
MISSING_BACKEND=0
for pkg in livekit openai "python-dotenv"; do
    if uv pip list 2>/dev/null | grep -q "^$pkg "; then
        VERSION=$(uv pip list 2>/dev/null | grep "^$pkg " | awk '{print $NF}')
        echo "  ✓ $pkg: $VERSION"
    else
        echo "  ❌ $pkg: MISSING"
        MISSING_BACKEND=1
    fi
done

# Check required files
echo ""
echo "✓ Checking Required Files..."
FILES=(
    "Vision.py"
    "server.py"
    "pdf_generate.py"
    "心身障碍者福祉手当認定申請書.json"
    ".env.local"
    "blank_form.pdf"
)

MISSING_FILES=0
for file in "${FILES[@]}"; do
    if [ -f "$BACKEND_DIR/$file" ]; then
        echo "  ✓ $file"
    elif [ "$file" = "blank_form.pdf" ]; then
        echo "  ⚠ blank_form.pdf: Not critical"
    else
        echo "  ❌ $file: MISSING"
        MISSING_FILES=1
    fi
done

# Check env files
echo ""
echo "✓ Checking Environment Files..."
if [ -f "$PROJECT_DIR/.env.local" ]; then
    echo "  ✓ Frontend .env.local"
else
    echo "  ❌ Frontend .env.local: MISSING"
fi

if [ -f "$BACKEND_DIR/.env.local" ]; then
    echo "  ✓ Backend .env.local"
else
    echo "  ❌ Backend .env.local: MISSING"
fi

# Check scripts
echo ""
echo "✓ Checking Startup Scripts..."
SCRIPTS=("start-all.sh" "start-backend-agent.sh" "start-frontend.sh")
for script in "${SCRIPTS[@]}"; do
    if [ -x "$PROJECT_DIR/$script" ]; then
        echo "  ✓ $script"
    else
        echo "  ❌ $script: Not executable"
    fi
done

# Final summary
echo ""
echo "=========================================="
if [ $MISSING_FRONTEND -eq 0 ] && [ $MISSING_BACKEND -eq 0 ] && [ $MISSING_FILES -eq 0 ]; then
    echo "✅ All systems ready!"
    echo ""
    echo "To start the application, run:"
    echo "  cd $PROJECT_DIR"
    echo "  ./start-all.sh"
    echo ""
    echo "Then visit: http://localhost:3001/form"
else
    echo "⚠️  Some components are missing. Installation incomplete."
    exit 1
fi
