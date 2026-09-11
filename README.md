# Cosmic Merge website

This repository is the authoritative source for the small static website. No framework or build step is required. `index.html`, `support.html`, and `privacy.html` share `assets/site.css` and local app-rendered images.

Preview locally with `python3 -m http.server 8766 --bind 127.0.0.1`. Validate structure, links, metadata, image sizes, and design-token contrast with `python3 scripts/validate.py`.

The page intentionally labels version 1.2 as a preview. Remove that banner and update release wording only after the app is actually available, its Rules 2 leaderboard exists, and signed iCloud behavior has been verified. There is no online daily leaderboard in this implementation.

Gameplay images are illustrative board fixtures rendered by the actual SpriteKit app in `SceneFlowTests.testRenderExampleBoardAndMenus`, exported from its test result bundle. They are not generated artwork or claims of recorded play sessions. Recapture after meaningful UI changes.

To update the game repository's generated documentation mirror, run its `scripts/sync_website.py --source /path/to/cosmic-merge-site`. Do not edit the mirrored HTML or assets independently. Hash checks detect drift.

The checked-in workflow validates changes; it does not deploy them. The existing GitHub Pages configuration continues to own publishing.

Validated September 10, 2026: all three pages pass the static checker. Browser checks at 1280 × 900, 390 × 844 and 360 × 800 covered internal navigation, image loading, readable layouts, keyboard focus/skip links, expandable help and keyboard scrolling of the controls table. The viewport override was reset after testing. This does not constitute a complete accessibility audit.
