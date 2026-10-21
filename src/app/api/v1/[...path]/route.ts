import { NextRequest } from "next/server";
import { backendUrl } from "@/src/lib/server-api";

const allowed = new Set([
  "GET health",
  "POST auth/login",
  "POST auth/logout",
  "GET auth/session",
  "GET usuarios",
  "GET tecnologia/conexao",
  "GET servico-social/cadastros",
  "GET servico-social/analises/resumo",
]);
async function forward(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const path = (await context.params).path.join("/");
  const safeHeaders = {
    "Cache-Control": "private, no-store",
    "X-Content-Type-Options": "nosniff",
  };
  if (!allowed.has(`${request.method} ${path}`))
    return Response.json(
      { detail: "Rota indisponível." },
      { status: 404, headers: safeHeaders },
    );
  const appOrigin = process.env.APP_ORIGIN || "http://localhost:3000";
  if (
    request.method === "POST" &&
    request.headers.get("origin") !== appOrigin
  ) {
    return Response.json(
      { detail: "Origem não autorizada." },
      { status: 403, headers: safeHeaders },
    );
  }
  let body: ArrayBuffer | undefined;
  if (request.method === "POST") {
    const reader = request.body?.getReader();
    const chunks: Uint8Array[] = [];
    let size = 0;
    if (reader) {
      while (true) {
        const part = await reader.read();
        if (part.done) break;
        size += part.value.byteLength;
        if (size > 16384) {
          await reader.cancel();
          return Response.json(
            { detail: "Requisição excessiva." },
            { status: 413, headers: safeHeaders },
          );
        }
        chunks.push(part.value);
      }
    }
    const bytes = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) {
      bytes.set(chunk, offset);
      offset += chunk.byteLength;
    }
    body = bytes.buffer;
  }
  const cookie = request.cookies.get("ac_social_ss")?.value;
  try {
    const response = await fetch(
      `${backendUrl()}/api/v1/${path}${request.nextUrl.search}`,
      {
        method: request.method,
        headers: {
          "Content-Type": "application/json",
          Origin: appOrigin,
          ...(cookie
            ? { Cookie: `ac_social_ss=${encodeURIComponent(cookie)}` }
            : {}),
        },
        body,
        cache: "no-store",
        redirect: "error",
        signal: AbortSignal.timeout(12000),
      },
    );
    const headers = new Headers(safeHeaders);
    headers.set("Content-Type", "application/json; charset=utf-8");
    for (const value of response.headers.getSetCookie())
      headers.append("Set-Cookie", value);
    return new Response(response.body, { status: response.status, headers });
  } catch {
    return Response.json(
      { detail: "Integração institucional indisponível." },
      { status: 503, headers: safeHeaders },
    );
  }
}
export const GET = forward;
export const POST = forward;
