// Login for the /admin editor (Decap CMS + GitHub) on Cloudflare Pages.
// Needs two settings in Cloudflare: GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET.
const page = (body, status = 200) =>
  new Response(body, { status, headers: { "content-type": "text/html;charset=utf-8", "cache-control": "no-store" } });

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/auth") {
      const state = crypto.randomUUID();
      const q = new URLSearchParams({
        client_id: env.GITHUB_CLIENT_ID,
        redirect_uri: url.origin + "/callback",
        scope: "repo,user",
        state,
      });
      return new Response(null, {
        status: 302,
        headers: {
          Location: "https://github.com/login/oauth/authorize?" + q,
          "Set-Cookie": "oauth_state=" + state + "; HttpOnly; Secure; Path=/; Max-Age=600; SameSite=Lax",
          "cache-control": "no-store",
        },
      });
    }

    if (url.pathname === "/callback") {
      const code = url.searchParams.get("code");
      const state = url.searchParams.get("state");
      const cookies = (request.headers.get("Cookie") || "").split(/;\s*/);
      let data = { message: "Login failed. Please close this window and try again." };
      let status = "error";
      if (code && state && cookies.includes("oauth_state=" + state)) {
        const r = await fetch("https://github.com/login/oauth/access_token", {
          method: "POST",
          headers: { "content-type": "application/json", accept: "application/json" },
          body: JSON.stringify({ client_id: env.GITHUB_CLIENT_ID, client_secret: env.GITHUB_CLIENT_SECRET, code }),
        });
        const d = await r.json();
        if (d.access_token) { data = { token: d.access_token, provider: "github" }; status = "success"; }
      }
      return page(`<!doctype html><meta charset="utf-8"><title>Signing in</title><p>Signing you in…</p><script>
(function () {
  var data = ${JSON.stringify(data)};
  function receive(e) {
    window.opener.postMessage("authorization:github:${status}:" + JSON.stringify(data), e.origin);
    window.removeEventListener("message", receive);
    window.close();
  }
  window.addEventListener("message", receive, false);
  window.opener.postMessage("authorizing:github", "*");
})();
</script>`);
    }

    return env.ASSETS.fetch(request);
  },
};
