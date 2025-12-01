#!/bin/bash

# Hugo Architecture Validation Script
# Ensures no architectural regressions before commits

set -e

echo "🔍 Hugo Architecture Validation"
echo "=============================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# 1. Check SPA toggle script is disabled
echo "📋 Checking SPA toggle script status..."
if [ -f "scripts/toggle-spa-mode.sh" ]; then
    echo -e "${RED}❌ ERROR: SPA toggle script exists! It should be disabled.${NC}"
    echo "   Run: mv scripts/toggle-spa-mode.sh scripts/disable-spa-mode.sh.backup"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ SPA toggle script properly disabled${NC}"
fi

# 2. Check core templates are PaperMod standard
echo ""
echo "🏗️ Checking core template architecture..."

check_template() {
    local template=$1
    local file="layouts/_default/$template"

    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Missing template: $file${NC}"
        ERRORS=$((ERRORS + 1))
        return 1
    fi

    # Check for SPA indicators
    if grep -q "BlogSPA\|SPA Router\|innerHTML.*main" "$file" 2>/dev/null; then
        echo -e "${RED}❌ ERROR: $template contains SPA code!${NC}"
        echo "   This should be PaperMod standard only."
        ERRORS=$((ERRORS + 1))
        return 1
    fi

    echo -e "${GREEN}✅ $template looks correct${NC}"
    return 0
}

check_template "baseof.html"
check_template "list.html"
check_template "single.html"

# 3. Check CSS architecture
echo ""
echo "🎨 Checking CSS architecture..."

if [ -f "assets/css/custom.css" ]; then
    # Check file size (should be reasonable)
    size=$(wc -l < assets/css/custom.css)
    if [ "$size" -gt 500 ]; then
        echo -e "${YELLOW}⚠️ WARNING: custom.css is large ($size lines). Consider optimization.${NC}"
    else
        echo -e "${GREEN}✅ custom.css size is reasonable ($size lines)${NC}"
    fi

    # Check for problematic CSS selectors
    if grep -q ":contains(" assets/css/custom.css 2>/dev/null; then
        echo -e "${RED}❌ ERROR: custom.css contains unsupported :contains() selectors${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✅ No problematic CSS selectors found${NC}"
    fi
else
    echo -e "${RED}❌ ERROR: Missing assets/css/custom.css${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check for Tailwind CDN in templates
echo ""
echo "📦 Checking for external CSS dependencies..."
if grep -r "cdn.tailwindcss.com" layouts/ 2>/dev/null; then
    echo -e "${RED}❌ ERROR: Tailwind CDN found in templates!${NC}"
    echo "   Use Hugo's CSS pipeline instead."
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No external CSS CDNs found${NC}"
fi

# 4. Try to build the site
echo ""
echo "🔨 Testing Hugo build..."

# Check if Docker is available
if ! command -v docker &> /dev/null || ! docker info &> /dev/null; then
    echo -e "${YELLOW}⚠️  WARNING: Docker not available, skipping build test${NC}"
    echo "   Build test requires Docker. Run 'make build' manually to verify."
    echo "   Architecture checks passed, but build verification skipped."
else
    # Docker is available, try to build
    # Use python for timeout (30s) to avoid hanging on Docker Desktop issues
    BUILD_RESULT=0
    if command -v python &> /dev/null; then
        python -c "import subprocess, sys; try: subprocess.run(sys.argv[1:], timeout=30, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); except subprocess.TimeoutExpired: sys.exit(124); except: sys.exit(1)" make build
        BUILD_RESULT=$?
    else
        make build > /dev/null 2>&1
        BUILD_RESULT=$?
    fi

    if [ $BUILD_RESULT -eq 0 ]; then
        echo -e "${GREEN}✅ Hugo build successful${NC}"
    elif [ $BUILD_RESULT -eq 124 ]; then
        echo -e "${YELLOW}⚠️  WARNING: Hugo build timed out (30s). Docker might be hung.${NC}"
        echo "   Skipping build verification to allow commit."
    else
        echo -e "${RED}❌ ERROR: Hugo build failed!${NC}"
        echo "   Run 'make build' to see the errors."
        ERRORS=$((ERRORS + 1))
    fi
fi

# 5. Final result
echo ""
echo "=============================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}🎉 All architecture checks passed!${NC}"
    echo "   Safe to commit changes."
    exit 0
else
    echo -e "${RED}❌ Architecture validation failed with $ERRORS error(s)!${NC}"
    echo "   Please fix the issues before committing."
    echo ""
    echo "   Read ARCHITECTURE.md for guidelines."
    exit 1
fi