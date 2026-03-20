#!/bin/bash

# Start only the Frontend (Next.js)
# Useful if backend is already running

PROJECT_DIR="/Users/y4l1/Documents/GDGJP-Hackathon/ai-privacy-amanuensis"

echo "🎨 Starting Frontend..."
echo "======================="

cd "$PROJECT_DIR"
npm run dev
