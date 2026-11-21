# hpimgai-clean-legal

Public legal documents for HPClean.

The Privacy Policy and Terms of Use in this repository are the approved English text. The HTML files present that same wording. Wording is not rewritten here. There is no build step, and the pages do not load external fonts, libraries, or trackers.

## Files

| File | Role |
| --- | --- |
| `index.html` | Short page that links to the Privacy Policy and Terms of Use |
| `privacy-policy.html` | Privacy Policy |
| `terms-of-use.html` | Terms of Use |
| `styles.css` | Shared layout, included locally |
| `privacy-policy-corrected.txt` | Approved Privacy Policy source |
| `terms-of-use-corrected.txt` | Approved Terms of Use source |
| `FUTURE-ADDITIONS-REMINDER-广告服务未来添加提醒.txt` | Internal developer reminder, stored under that filename with its text unchanged. It is not the current Privacy Policy and it is not linked from the site. |
| `legal-documents-changes.txt` | Local correction log for the two approved text edits. Stored unchanged and not linked from the site. |
| `.nojekyll` | Disables Jekyll so GitHub Pages serves these files as-is |

## GitHub Pages

These files are ready to publish from the `main` branch root. Publishing still has to be turned on in the GitHub website. This repository does not enable Pages by itself, and this README does not mean a live site already exists.

1. Open the repository on GitHub.
2. Go to **Settings**, then **Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Choose branch **main** and folder **/ (root)**.
5. Save.

No install, package manager, or workflow is required. After GitHub finishes that deployment, the root files are the site:

- `/` or `/index.html`
- `/privacy-policy.html`
- `/terms-of-use.html`

## Updating the legal text

Replace a page only from a new approved source. Keep the sentences the same as that source. `tests/check_legal_html.py` checks that the visible article text matches the `.txt` sources aside from whitespace, list markers, the underscore dividers, and the email link.
