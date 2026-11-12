# Mehshan's website, with a login editor

How it works: the site is built from `content/site.json` and the `images` folder.
The editor at `/admin` changes those files on GitHub, and Netlify rebuilds the site by itself in about a minute.

## One-time setup

1. Create a free account at github.com.
2. Create a new repository named `mehshan-site` (public or private). Choose "uploading an existing file" and upload everything from this folder (the contents, not the zip). Commit.
3. `admin/config.yml` already points to `mehshan3112/mehshan-site`, so name the repository exactly `mehshan-site` under your account.
4. Create a GitHub OAuth app: GitHub > Settings > Developer settings > OAuth Apps > New OAuth App.
   - Homepage URL: your Netlify site address (step 5)
   - Authorization callback URL: https://api.netlify.com/auth/done
   Copy the Client ID, and generate and copy a Client Secret.
5. Netlify: Add new site > Import an existing project > GitHub > pick `mehshan-site`. Settings are read from `netlify.toml`, so just press Deploy.
6. Netlify: Site configuration > Access & security > OAuth > Install provider > GitHub. Paste the Client ID and Client Secret.

## Everyday use

Open `your-site.netlify.app/admin`, press "Login with GitHub", edit, and press Publish. The public site shows no login anywhere, and only your GitHub account can edit.

Image upload: inside the editor use "Choose an image" and upload a new file.
