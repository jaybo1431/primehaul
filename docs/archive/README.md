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
