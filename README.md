# fennwild-site

Public website for **Fennwild** by Reedlight Games, served by GitHub Pages at
https://bstotmeister.github.io/fennwild-site — privacy policy, terms, support, press kit and the
Android play-test sign-up.

- `src/` — page templates (`{{key}}` placeholders, `{{include:partial}}`, `<!-- if:key -->` blocks)
- `site.config.json` — every public value: store links, contact email, tester links
- `tools/build.py` — renders `_site/` (run locally: `python3 tools/build.py && python3 -m http.server -d _site`)
- `.github/workflows/site.yml` — builds and deploys on every push to `main`

Repository → Settings → Pages → Source must be **GitHub Actions** once, after the first push.

Game source lives in the private `fennwild` repository.
