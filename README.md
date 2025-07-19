
```
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "Wiki Search" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "WikiSearch.app" 200 190 \
  --hide-extension "WikiSearch.app" \
  --app-drop-link 600 185 \
  "WikiSearch.dmg" \
  "./dist/WikiSearch.app"
  ```