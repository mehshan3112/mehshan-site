const SITE_ORIGIN = "https://mehshan.pages.dev";
const CALLBACK_URL = `${SITE_ORIGIN}/api/callback`;

export async function onRequest({ request, env }) {
  if (request.method !== "GET") {
    return new Response("Method not allowed", {
      status: 405,
      headers: { Allow: "GET" }
    });
  }

  if (!env.GITHUB_CLIENT_ID) {
    return new Response("Missing GITHUB_CLIENT_ID Cloudflare variable.", {
      status: 500
    });
  }

  const state = crypto.randomUUID();

  const authorizeUrl = new URL(
    "https://github.com/login/oauth/authorize"
  );

  authorizeUrl.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
  authorizeUrl.searchParams.set("redirect_uri", CALLBACK_URL);
  authorizeUrl.searchParams.set("scope", "public_repo read:user");
  authorizeUrl.searchParams.set("state", state);

  return new Response(null, {
    status: 302,
    headers: {
      Location: authorizeUrl.toString(),
      "Set-Cookie":
        `decap_oauth_state=${state}; Path=/api; HttpOnly; Secure; SameSite=Lax; Max-Age=600`,
      "Cache-Control": "no-store"
    }
  });
}
