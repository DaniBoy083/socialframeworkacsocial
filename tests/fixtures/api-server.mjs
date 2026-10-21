// Isolated HTTP fixture for frontend tests. Never imported by the application.
import { createServer } from "node:http";
const clinicActor = {
  id: "synthetic-professional",
  name: "Pessoa de teste",
  email: "test@example.invalid",
};
createServer((request, response) => {
  response.setHeader("Content-Type", "application/json");
  response.setHeader("Cache-Control", "private, no-store");
  const token = request.headers.cookie || "";
  const technology = token.includes("fixture-technology");
  const social = token.includes("fixture-social");
  if (request.url === "/health") return response.end('{"ok":true}');
  if (!technology && !social) {
    response.statusCode = 401;
    return response.end('{"detail":"unauthorized"}');
  }
  if (request.url === "/api/v1/auth/session")
    return response.end(
      JSON.stringify({
        authenticated: true,
        actor: {
          ...clinicActor,
          teams: [technology ? "Tecnologia" : "Equipe sintética"],
          isTechnology: technology,
          permissions: social ? ["registrations:read", "analytics:read"] : [],
        },
      }),
    );
  if (request.url.startsWith("/api/v1/servico-social/cadastros"))
    return response.end('{"items":[],"hasMore":false}');
  if (request.url === "/api/v1/tecnologia/conexao")
    return response.end(
      JSON.stringify({
        database: "connected",
        authTablesPresent: true,
        identityContractVerified: false,
        socialRecordsReady: false,
        storageReady: false,
        latencyMs: 1,
        accessPolicyApproved: false,
      }),
    );
  response.statusCode = 503;
  response.end('{"detail":"pending"}');
}).listen(18001, "127.0.0.1");
