#!/bin/bash
# 🧹 PrimeHaul Cleanup Script
# Archives old files and removes obsolete code
# SAFE: Archives files instead of deleting them

set -e  # Exit on error

echo "🧹 PrimeHaul Stack Cleanup"
echo "=========================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Must run from primehaul-os root directory"
    exit 1
fi

echo "📋 This script will:"
echo "  1. Create docs/archive folders"
echo "  2. Move old planning docs to archive"
echo "  3. Move marketplace docs to archive (not using yet)"
echo "  4. Remove obsolete template files"
echo "  5. Archive old migration scripts"
echo ""
echo "⚠️  Files will be ARCHIVED, not deleted (safe to recover)"
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Cleanup cancelled"
    exit 0
fi

echo ""
echo "🚀 Starting cleanup..."
echo ""

# Step 1: Create archive folders
echo "📁 Creating archive folders..."
mkdir -p docs/archive/planning
mkdir -p docs/archive/marketplace
mkdir -p docs/archive/old-migrations
mkdir -p docs/archive/old-templates
echo -e "${GREEN}✓${NC} Archive folders created"

# Step 2: Archive planning docs
echo ""
echo "📦 Archiving planning documentation..."
FILES_TO_ARCHIVE_PLANNING=(
    "INVESTOR_PITCH.md"
    "LAUNCH_TODAY.md"
    "REALISTIC_LAUNCH_STRATEGY.md"
    "PRE_LAUNCH_AUDIT.md"
    "TEST_TODAY_QUICK.md"
    "SIMULATION_RESULTS.md"
    "DEPLOYMENT_STEP_BY_STEP.md"
    "QUICK_FIX_MARKETPLACE.md"
)

for file in "${FILES_TO_ARCHIVE_PLANNING[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" docs/archive/planning/
        echo -e "${GREEN}✓${NC} Archived: $file"
    fi
done

# Step 3: Archive marketplace docs
echo ""
echo "📦 Archiving marketplace documentation..."
FILES_TO_ARCHIVE_MARKETPLACE=(
    "MARKETPLACE_GUIDE.md"
    "PARTNER_LAUNCH_PLAN.md"
    "PARTNER_PARTNERSHIP_PROPOSAL.md"
    "PARTNER_ROLE_FINAL.md"
    "PARTNER_START_HERE.md"
    "PARTNER_TEMPLATES.md"
)

for file in "${FILES_TO_ARCHIVE_MARKETPLACE[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" docs/archive/marketplace/
        echo -e "${GREEN}✓${NC} Archived: $file"
    fi
done

# Step 4: Archive obsolete templates
echo ""
echo "📦 Archiving obsolete templates..."
TEMPLATES_TO_ARCHIVE=(
    "app/templates/landing_page.html"
    "app/templates/start.html"
    "app/templates/test_map.html"
    "app/templates/marketplace_dashboard.html"
    "app/templates/marketplace_job_detail.html"
    "app/templates/marketplace_landing.html"
    "app/templates/marketplace_quotes.html"
)

for file in "${TEMPLATES_TO_ARCHIVE[@]}"; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        mv "$file" docs/archive/old-templates/
        echo -e "${GREEN}✓${NC} Archived: $filename"
    fi
done

# Step 5: Archive old migration scripts
echo ""
echo "📦 Archiving old migration scripts..."
SCRIPTS_TO_ARCHIVE=(
    "add_move_date_column.py"
    "create_tables.py"
)

for file in "${SCRIPTS_TO_ARCHIVE[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" docs/archive/old-migrations/
        echo -e "${GREEN}✓${NC} Archived: $file"
    fi
done

# Step 6: Create archive README
echo ""
echo "📝 Creating archive documentation..."
cat > docs/archive/README.md << 'EOF'
# Archived Files

This folder contains files that were removed during codebase cleanup but kept for reference.

## Folders

### planning/
Old planning documents, launch strategies, and testing notes. Kept for historical reference.

### marketplace/
Marketplace and partner integration documentation. Not currently in use but may be needed in future.

### old-migrations/
One-time migration scripts that are now handled by Alembic migrations.

### old-templates/
Obsolete HTML templates that have been replaced by newer versions:
- `landing_page.html` → Replaced by `landing_primehaul_uk.html`
- `start.html` → Replaced by `start_v2.html`
- `marketplace_*.html` → Not currently in use

## Recovery

All files in this archive can be restored if needed:
```bash
# Example: Restore a file
cp docs/archive/planning/INVESTOR_PITCH.md ./
```

## Cleanup

After confirming everything works for 1-2 weeks, you can safely delete this entire archive:
```bash
# Only do this if you're 100% sure you don't need these files
rm -rf docs/archive
```

---

**Archived**: January 2026
**Reason**: Codebase cleanup and streamlining
EOF

echo -e "${GREEN}✓${NC} Archive README created"

# Step 7: Summary
echo ""
echo "=================================="
echo "✅ Cleanup Complete!"
echo "=================================="
echo ""
echo "📊 Summary:"
echo "  • Planning docs archived: ${#FILES_TO_ARCHIVE_PLANNING[@]}"
echo "  • Marketplace docs archived: ${#FILES_TO_ARCHIVE_MARKETPLACE[@]}"
echo "  • Templates archived: ${#TEMPLATES_TO_ARCHIVE[@]}"
echo "  • Scripts archived: ${#SCRIPTS_TO_ARCHIVE[@]}"
echo ""
echo "📁 Archived files are in: docs/archive/"
echo ""
echo "🎯 Next Steps:"
echo "  1. Test the application still works"
echo "  2. Deploy to staging and verify"
echo "  3. After 1 week, delete docs/archive if all good"
echo ""
echo "💡 To restore a file:"
echo "   cp docs/archive/[folder]/[file] ./"
echo ""
echo "🎉 Your codebase is now clean and streamlined!"
