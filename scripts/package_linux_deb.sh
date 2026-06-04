#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-$(cat "$PROJECT_ROOT/VERSION")}"
DIST="$PROJECT_ROOT/dist"
RUNTIME="$DIST/NDIM Engine App"
PACKAGE_ROOT="$DIST/deb/ndim-engine"
DEB="$DIST/ndim-engine_${VERSION}_amd64.deb"

if [[ ! -d "$RUNTIME" ]]; then
  echo "Build the PyInstaller runtime first: USE_VENV=1 ./scripts/build_desktop.sh --clean" >&2
  exit 1
fi

rm -rf "$PACKAGE_ROOT" "$DEB"
mkdir -p "$PACKAGE_ROOT/DEBIAN" "$PACKAGE_ROOT/opt/ndim-engine" "$PACKAGE_ROOT/usr/share/applications" "$PACKAGE_ROOT/usr/bin"
cp -R "$RUNTIME/." "$PACKAGE_ROOT/opt/ndim-engine/"

cat > "$PACKAGE_ROOT/DEBIAN/control" <<EOF
Package: ndim-engine
Version: $VERSION
Section: science
Priority: optional
Architecture: amd64
Maintainer: NDIM Engine
Description: Local-first narrative evidence, modelling, and policy workflow.
EOF

cat > "$PACKAGE_ROOT/usr/bin/ndim-engine" <<'EOF'
#!/usr/bin/env bash
exec "/opt/ndim-engine/NDIM Engine" "$@"
EOF
chmod +x "$PACKAGE_ROOT/usr/bin/ndim-engine"

cat > "$PACKAGE_ROOT/usr/share/applications/ndim-engine.desktop" <<'EOF'
[Desktop Entry]
Name=NDIM Engine
Comment=Local-first narrative evidence, modelling, and policy workflow
Exec=ndim-engine
Terminal=false
Type=Application
Categories=Science;Education;
EOF

dpkg-deb --build "$PACKAGE_ROOT" "$DEB"
cp "$PROJECT_ROOT/docs/ALPHA_TESTER_README.md" "$DIST/ALPHA_TESTER_README.md"
(
  cd "$DIST"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$(basename "$DEB")" ALPHA_TESTER_README.md > SHA256SUMS.txt
  else
    shasum -a 256 "$(basename "$DEB")" ALPHA_TESTER_README.md > SHA256SUMS.txt
  fi
)
echo "Created $DEB"
