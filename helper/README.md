# In-game helper

Your session checklist in a browser tab, with an **Open in game** button on every item (it opens that item's
market window in your EVE client) and a checkbox to tick as you go. **Copy session report** puts your online
times and how far you got on the clipboard, ready to paste to Claude.

## One-time setup (about 5 minutes)
1. Install Python 3 if you don't have it: python.org/downloads (on the first screen of the Windows installer,
   tick "Add python.exe to PATH").
2. Download `ingame.py` from this folder: open the file on GitHub, click the download icon (⤓), and save it,
   e.g. to your Desktop.

## Each session
1. Log the **trading character** into EVE.
2. Run the helper by double-clicking `ingame.py`, or in a terminal: `python ingame.py`.
   A browser tab opens at http://localhost:8765.
3. First time only: click **Log in with EVE**, pick the trading character, and approve. The only permission it
   asks for is opening windows in your client. The token stays on your PC in `~/.isk-machine/`.
4. Click **Start session**, then work down the list: **Open in game** → do the step → tick the box.
5. At the end, click **Copy session report** and paste it to Claude.

## If something goes wrong
- "EVE refused the login": save the app's `client_secret` (from developers.eveonline.com) as the only line of
  `~/.isk-machine/client_secret.txt` and log in again.
- "ESI said 401/403": the trading character isn't logged into EVE, or the login expired. Click Log in again.
- Once the repo is private, save a GitHub token with read access as `~/.isk-machine/github_token.txt`.
