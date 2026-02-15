# Website Quick Edit Guide

This site is deployed from `site/` using GitHub Actions.

## Edit Content
- Update project/skills/timeline data in `site/script.js`.
- Update layout/content blocks in `site/index.html`.
- Update theme and styling in `site/styles.css`.

## Deploy
- Push to `main`.
- Workflow: `.github/workflows/deploy-site.yml`
- GitHub Pages URL pattern:
  - `https://<your-github-username>.github.io/<repo-name>/`

## One-Time Repo Setting
- In GitHub repo settings:
  - `Settings -> Pages -> Build and deployment -> Source: GitHub Actions`
