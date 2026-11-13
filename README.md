# Mehshan's website (Cloudflare Pages + login editor)

The site is built from `site.json` and the pictures. The editor at `/admin` changes those files on GitHub; Cloudflare then rebuilds the site by itself in about a minute.
Files can sit loose at the top level of the repository (no folders needed).

## Cloudflare setup (one time)

1. Cloudflare dashboard > Workers & Pages > Create > Pages > Connect to Git > GitHub > pick `mehshan-site`.
2. Project name: `mehshan` (the address becomes https://mehshan.pages.dev). If it is taken, use another name and change `site_url` and `base_url` (see below).
3. Build settings: Framework preset None, Build command `python3 build.py`, Build output directory `dist`. Save and Deploy.
4. GitHub OAuth app (GitHub > Settings > Developer settings > OAuth Apps): set Homepage URL `https://mehshan.pages.dev` and Authorization callback URL `https://mehshan.pages.dev/callback`. Keep the Client ID and Client Secret.
5. Cloudflare: your Pages project > Settings > Variables and Secrets > add `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` (for Production). Then Deployments > Retry deployment, so the new settings take effect.
6. Open https://mehshan.pages.dev/admin and press Login with GitHub.

If your Cloudflare address is different, edit `base_url` in `config.yml` and `site_url` in `site.json` (or in the editor, "Website address").

## Logos and photos

In the editor: Experience and Leadership entries have a Logo field (upload the image). Without a logo, the letters from "Letters shown if there is no logo" appear in a coloured badge.
Each extracurricular entry has a Photos list: replace the "Photo slot" pictures with real ones.
