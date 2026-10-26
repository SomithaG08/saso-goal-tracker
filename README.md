# Saso's Goal Tracker

Personal goal tracker (daily → yearly goals, streaks, reflections, daily learning), installable on a phone as a full-screen app.

Data is stored on the device. Use the ⤓ button in the app to download or restore a backup.

## Notion sync

Every night (and on every push, or when you press **Actions → Sync Notion and deploy app → Run workflow**), GitHub reads the
*Vocabulary* and *Questions* tables under the Notion page **Goal Tracker — Learn Sync** and publishes them as `content.json`.
The app loads it on open and with **Learn → Sync from Notion**.

Setup (once):
1. Notion: create an internal integration at https://www.notion.so/profile/integrations and copy its secret.
2. Notion: open **Goal Tracker — Learn Sync** → ••• → **Connections** → add the integration.
3. GitHub: **Settings → Secrets and variables → Actions → New repository secret**, name `NOTION_TOKEN`, paste the secret.
4. GitHub: **Settings → Pages → Source: GitHub Actions**.
5. GitHub: **Actions → Sync Notion and deploy app → Run workflow**.
