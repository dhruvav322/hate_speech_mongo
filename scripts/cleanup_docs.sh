#!/bin/bash
# Move duplicate documentation files to docs/archive/

mkdir -p docs/archive

# Move session/status docs
mv -f BACKEND_RUNNING.md BACKEND_START.md START_BACKEND.md START_BACKEND_NOW.md QUICK_FIX_OFFLINE.md STATUS_UPDATE.md docs/archive/ 2>/dev/null || true

# Move setup guides (keep main README)
mv -f SETUP_GUIDE.md SETUP_INSTRUCTIONS.md FRONTEND_NEXTJS_SETUP.md REACT_FRONTEND_SETUP.md QUICKSTART.md docs/archive/ 2>/dev/null || true

# Move summaries
mv -f CHANGES_SUMMARY.md COMPLETED_WORK.md SESSION_SUMMARY.md GIT_PUSH_SUMMARY.md DEPLOYMENT_SUMMARY.md docs/archive/ 2>/dev/null || true

# Move audits/reviews
mv -f SCALABILITY_AUDIT.md SCALABILITY_IMPLEMENTATION.md SECURITY_AUDIT.md SUMMARY_SECURITY_REVIEW.md OPTIMIZATION_CHECKLIST.md docs/archive/ 2>/dev/null || true

# Move CORS fixes (historical)
mv -f CORS_FIX.md CORS_FINAL_FIX.md docs/archive/ 2>/dev/null || true

# Move other guides
mv -f DEPLOYMENT_GUIDE.md MODEL_STATUS_REPORT.md MODEL_ACCURACY_SUMMARY.md PROTECT_YOUR_PROJECT.md MAKE_IT_PUBLIC.md VSCODE_SETUP_GUIDE.md docs/archive/ 2>/dev/null || true

# Keep these in root: README.md, LICENSE, IMPLEMENTATION_GUIDE.md, TEST_CASES.md

echo "✅ Documentation cleanup complete. Files moved to docs/archive/"
