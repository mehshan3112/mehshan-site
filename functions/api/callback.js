const SITE_ORIGIN = "https://mehshan.pages.dev";
const CALLBACK_URL = `${SITE_ORIGIN}/api/callback`;
const ALLOWED_GITHUB_USER = "mehshan3112";
const REPOSITORY = "mehshan3112/mehshan-site";

function readCookie(request, name) {
  const cookieHeader = request.headers.get("Cookie") || "";
  for (const part of cookieHeader.split(";")) {
    const item = part.trim();
    const separator = item.indexOf("=");
    if (separator === -1) continue;

    if (item.slice(0, separator) === name) {
      return item.slice(separator + 1);
    }
  }
  return null;
}

function popupResponse(status, content, clearStateCookie = true) {
  // Safely encode the Decap message before embedding it in inline JavaScript.
  const message =
    `authorization:github:${status}:${JSON.stringify(content)}`;
  const safeMessage = JSON.stringify(message).replace(/</g, "\\u003c");
  const safeOrigin = JSON.stringify(SITE_ORIGIN);

  const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GitHub authentication</title>
</head>
<body>
  <p>Completing GitHub authentication. You can close this window if it does not close automatically.</p>
  <script>
    (() => {
      const openerWindow = window.opener;
      const expectedOrigin = ${safeOrigin};
      const payload = ${safeMessage};

      if (!openerWindow) {
        document.body.textContent =
          "The CMS login window was not found. Close this tab and try again.";
        return;
      }

      function receiveMessage(event) {
        if (event.source !== openerWindow) return;
        if (event.origin !== expectedOrigin) return;

        window.removeEventListener("message", receiveMessage);
        openerWindow.postMessage(payload, expectedOrigin);
        window.close();
      }

      window.addEventListener("message", receiveMessage, false);
      openerWindow.postMessage("authorizing:github", expectedOrigin);
    })();
  </script>
</body>
</html>`;

  const headers = new Headers({
    "Content-Type": "text/html; charset=UTF-8",
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer"
  });

  if (clearStateCookie) {
    headers.append(
      "Set-Cookie",
      "decap_oauth_state=; Path=/api; HttpOnly; Secure; SameSite=Lax; Max-Age=0"
    );
  }

  return new Response(html, { status: 200, headers });
}

export async function onRequest({ request, env }) {
  if (request.method !== "GET") {
    return new Response("Method not allowed", {
      status: 405,
      headers: { Allow: "GET" }
    });
  }

  const url = new URL(request.url);
  const stateFromQuery = url.searchParams.get("state");
  const stateFromCookie = readCookie(request, "decap_oauth_state");
  const code = url.searchParams.get("code");
  const githubError = url.searchParams.get("error");

  if (!stateFromQuery || !stateFromCookie || stateFromQuery !== stateFromCookie) {
    return popupResponse("error", {
      message: "OAuth state validation failed. Close this window and try again."
    });
  }

  if (githubError) {
    return popupResponse("error", {
      message: githubError === "access_denied"
        ? "GitHub access was cancelled."
        : "GitHub returned an authentication error."
    });
  }

  if (!code || !env.GITHUB_CLIENT_ID || !env.GITHUB_CLIENT_SECRET) {
    return popupResponse("error", {
      message: "The OAuth code or Cloudflare credentials are missing."
    });
  }

  try {
    const tokenResponse = await fetch(
      "https://github.com/login/oauth/access_token",
      {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "User-Agent": "mehshan-portfolio-decap-cms"
        },
        body: JSON.stringify({
          client_id: env.GITHUB_CLIENT_ID,
          client_secret: env.GITHUB_CLIENT_SECRET,
          code,
          redirect_uri: CALLBACK_URL
        })
      }
    );

    const tokenData = await tokenResponse.json();

    if (!tokenResponse.ok || !tokenData.access_token) {
      console.error("GitHub token exchange failed:", tokenData.error || tokenResponse.status);
      return popupResponse("error", {
        message: "GitHub could not complete the token exchange. Check the OAuth callback URL and credentials."
      });
    }

    const accessToken = tokenData.access_token;

    // Only allow the repository owner to enter this private admin editor.
    const userResponse = await fetch("https://api.github.com/user", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "mehshan-portfolio-decap-cms"
      }
    });

    if (!userResponse.ok) {
      return popupResponse("error", {
        message: "GitHub could not verify the signed-in account."
      });
    }

    const user = await userResponse.json();

    if (user.login !== ALLOWED_GITHUB_USER) {
      return popupResponse("error", {
        message: "This CMS is restricted to its repository owner."
      });
    }

    // Confirm the account has push access to the content repository.
    const repoResponse = await fetch(
      `https://api.github.com/repos/${REPOSITORY}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
          "User-Agent": "mehshan-portfolio-decap-cms"
        }
      }
    );

    if (!repoResponse.ok) {
      return popupResponse("error", {
        message: "Could not verify access to the portfolio repository."
      });
    }

    const repo = await repoResponse.json();

    if (!repo.permissions || repo.permissions.push !== true) {
      return popupResponse("error", {
        message: "The signed-in GitHub account does not have push access to the portfolio repository."
      });
    }

    return popupResponse("success", {
      token: accessToken,
      provider: "github"
    });
  } catch (error) {
    console.error("OAuth callback failed:", error);
    return popupResponse("error", {
      message: "The authentication service encountered an unexpected error. Please try again."
    });
  }
}
