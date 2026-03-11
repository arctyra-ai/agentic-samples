#!/bin/bash

echo "🔍 AI Readiness Scorecard - Verification Script"
echo "================================================"
echo ""

# Check directory structure
echo "✓ Checking directory structure..."
test -f package.json && echo "  ✓ package.json exists"
test -f README.md && echo "  ✓ README.md exists"
test -d app/scorecard && echo "  ✓ app/scorecard directory exists"
test -d app/scorecard/components && echo "  ✓ components directory exists"
test -d app/scorecard/lib && echo "  ✓ lib directory exists"
echo ""

# Check for Arctyra references
echo "✓ Checking for removed references..."
if grep -r "Arctyra" app/ --include="*.tsx" --include="*.ts" 2>/dev/null | grep -v "Part of Arctyra Agentic AI Training" | grep -v "agentic-samples" > /dev/null; then
  echo "  ⚠️  Found Arctyra references in app/"
  grep -r "Arctyra" app/ --include="*.tsx" --include="*.ts" | grep -v "Part of Arctyra Agentic AI Training" | grep -v "agentic-samples"
else
  echo "  ✓ No Arctyra references found"
fi

if grep -r "Amrit DePaulo" app/ --include="*.tsx" --include="*.ts" 2>/dev/null > /dev/null; then
  echo "  ⚠️  Found Amrit DePaulo references"
else
  echo "  ✓ No Amrit DePaulo references found"
fi

if grep -r "arctyra-gwbzwl" app/ --include="*.tsx" --include="*.ts" 2>/dev/null > /dev/null; then
  echo "  ⚠️  Found Cal.com booking URL"
else
  echo "  ✓ No Cal.com booking URL found"
fi
echo ""

# Check that key files exist
echo "✓ Checking component files..."
for file in ScorecardApp ScorecardLanding EmailGate QuestionFlow DimensionIntro ScorecardResults ScoreGauge DimensionalChart; do
  test -f "app/scorecard/components/${file}.tsx" && echo "  ✓ ${file}.tsx exists" || echo "  ✗ ${file}.tsx missing"
done
echo ""

echo "✓ Checking lib files..."
for file in brand types questions scoring interpretations email-validation analytics; do
  test -f "app/scorecard/lib/${file}.ts" && echo "  ✓ ${file}.ts exists" || echo "  ✗ ${file}.ts missing"
done
echo ""

# Check that integration files are removed
echo "✓ Checking removed integrations..."
test ! -f app/scorecard/lib/hubspot.ts && echo "  ✓ hubspot.ts removed" || echo "  ⚠️  hubspot.ts still exists"
test ! -f app/scorecard/lib/emails.ts && echo "  ✓ emails.ts removed" || echo "  ⚠️  emails.ts still exists"
test ! -f app/scorecard/lib/email-scheduler.ts && echo "  ✓ email-scheduler.ts removed" || echo "  ⚠️  email-scheduler.ts still exists"
test ! -d app/api/scorecard && echo "  ✓ API routes removed" || echo "  ⚠️  API routes still exist"
echo ""

echo "✓ Build status..."
test -d .next && echo "  ✓ Build completed successfully" || echo "  ⚠️  Build directory not found"
echo ""

echo "================================================"
echo "Verification complete!"
echo ""
echo "To start the dev server:"
echo "  pnpm dev"
echo ""
echo "Then open: http://localhost:3000/scorecard"
