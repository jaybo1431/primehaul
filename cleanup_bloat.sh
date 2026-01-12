#!/bin/bash

# 🧹 Cleanup Bloat - Remove unnecessary documentation files

echo "🧹 Cleaning up bloat and unnecessary files..."
echo ""

# Create archive directory for documentation
mkdir -p _archive_docs

# Move bloat documentation to archive
echo "📦 Archiving old documentation..."
mv DEPLOYMENT_STEP_BY_STEP.md _archive_docs/ 2>/dev/null
mv INVESTOR_PITCH.md _archive_docs/ 2>/dev/null
mv LAUNCH_TODAY.md _archive_docs/ 2>/dev/null
mv MARKETPLACE_GUIDE.md _archive_docs/ 2>/dev/null
mv PARTNER_LAUNCH_PLAN.md _archive_docs/ 2>/dev/null
mv PARTNER_PARTNERSHIP_PROPOSAL.md _archive_docs/ 2>/dev/null
mv PARTNER_ROLE_FINAL.md _archive_docs/ 2>/dev/null
mv PARTNER_START_HERE.md _archive_docs/ 2>/dev/null
mv PARTNER_TEMPLATES.md _archive_docs/ 2>/dev/null
mv PRE_LAUNCH_AUDIT.md _archive_docs/ 2>/dev/null
mv QUICK_FIX_MARKETPLACE.md _archive_docs/ 2>/dev/null
mv REALISTIC_LAUNCH_STRATEGY.md _archive_docs/ 2>/dev/null
mv SIMULATION_RESULTS.md _archive_docs/ 2>/dev/null
mv TEST_TODAY_QUICK.md _archive_docs/ 2>/dev/null
mv CLEANUP_AUDIT.md _archive_docs/ 2>/dev/null
mv PRIMEHAUL_UK_DEPLOYMENT.md _archive_docs/ 2>/dev/null
mv QUICK_START_STAGING.md _archive_docs/ 2>/dev/null
mv RAILWAY_DEPLOY_NOW.md _archive_docs/ 2>/dev/null
mv STAGING_DEPLOYMENT_GUIDE.md _archive_docs/ 2>/dev/null
mv UX_IMPROVEMENTS_SUMMARY.md _archive_docs/ 2>/dev/null
mv WEBSITE_READY.md _archive_docs/ 2>/dev/null
mv BRAND_IDENTITY_GUIDE.md _archive_docs/ 2>/dev/null
mv BUSINESS_MODEL_PRICING_STRATEGY.md _archive_docs/ 2>/dev/null
mv LOGO_CONCEPTS.md _archive_docs/ 2>/dev/null
mv LOGO_FINAL_PACKAGE.md _archive_docs/ 2>/dev/null
mv LOGO_PREVIEW.html _archive_docs/ 2>/dev/null
mv PRIMEHAUL_OS_ONEPAGER.html _archive_docs/ 2>/dev/null
mv PRIMEHAUL_OS_ONEPAGER.md _archive_docs/ 2>/dev/null
mv STACK_ENHANCEMENT_RECOMMENDATIONS.md _archive_docs/ 2>/dev/null

# Remove old test scripts that are replaced by FRESH_START.py
echo "🗑️  Removing old test scripts..."
rm -f create_test_company.py
rm -f reset_test_data.py
rm -f check_user.py
rm -f create_pricing_config.py
rm -f create_tables.py
rm -f add_move_date_column.py

# Keep only essential files:
# - reset_database.py (useful for emergencies)
# - init_db.py (used by Railway)
# - FRESH_START.py (new comprehensive script)
# - TESTING_GUIDE.md (new testing guide)
# - README.md (keep the main readme)

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📁 Archived documentation moved to: _archive_docs/"
echo "🗑️  Removed redundant test scripts"
echo "✨ Kept only essential files"
echo ""
echo "📋 Essential files remaining:"
echo "   - README.md (main documentation)"
echo "   - TESTING_GUIDE.md (for demos and testing)"
echo "   - FRESH_START.py (complete database reset + test data)"
echo "   - init_db.py (Railway deployment)"
echo "   - reset_database.py (emergency reset)"
echo ""
