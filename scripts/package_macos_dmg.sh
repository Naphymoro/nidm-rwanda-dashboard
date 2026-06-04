#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "macOS DMG packaging must run on macOS." >&2
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-$(cat "$PROJECT_ROOT/VERSION")}"
DIST="$PROJECT_ROOT/dist"
APP_DIR="$DIST/NDIM Engine.app"
RUNTIME="$DIST/NDIM Engine App"
DMG="$DIST/NDIM-Engine-$VERSION.dmg"

if [[ ! -d "$RUNTIME" ]]; then
  echo "Build the PyInstaller runtime first: USE_VENV=1 ./scripts/build_desktop.sh --clean" >&2
  exit 1
fi

rm -rf "$APP_DIR" "$DMG"
mkdir -p "$APP_DIR/Contents/MacOS" "$APP_DIR/Contents/Resources"
cp -R "$RUNTIME" "$APP_DIR/Contents/Resources/NDIM Engine Runtime"

cat > "$APP_DIR/Contents/MacOS/NDIM Engine" <<'EOF'
#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")/../Resources/NDIM Engine Runtime" && pwd)"
exec "$DIR/NDIM Engine"
EOF
chmod +x "$APP_DIR/Contents/MacOS/NDIM Engine"

cat > "$APP_DIR/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>NDIM Engine</string>
  <key>CFBundleDisplayName</key><string>NDIM Engine</string>
  <key>CFBundleIdentifier</key><string>org.ndim.engine</string>
  <key>CFBundleVersion</key><string>$VERSION</string>
  <key>CFBundleShortVersionString</key><string>$VERSION</string>
  <key>CFBundleExecutable</key><string>NDIM Engine</string>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
</dict>
</plist>
EOF

hdiutil create -volname "NDIM Engine" -srcfolder "$APP_DIR" -ov -format UDZO "$DMG"
cp "$PROJECT_ROOT/docs/ALPHA_TESTER_README.md" "$DIST/ALPHA_TESTER_README.md"
(
  cd "$DIST"
  shasum -a 256 "$(basename "$DMG")" ALPHA_TESTER_README.md > SHA256SUMS.txt
)
echo "Created $DMG"
