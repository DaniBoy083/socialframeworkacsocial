import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import {
  formatLastAppointment,
  whatsappContact,
} from "../src/features/registrations/formatters";

test("login institucional acessível e responsivo", async ({ page }, info) => {
  await page.goto("/login");
  await expect(
    page.getByRole("heading", { name: "Entrar na plataforma" }),
  ).toBeVisible();
  await expect(page.getByRole("textbox", { name: "E-mail" })).toBeVisible();
  await expect(page.getByLabel("Senha", { exact: true })).toHaveAttribute(
    "type",
    "password",
  );
  await expect(page.locator("footer")).toHaveCount(1);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  const audit = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(audit.violations).toEqual([]);
  await page.screenshot({
    path: `output/screenshots/login-${info.project.name}.png`,
    fullPage: true,
    animations: "disabled",
  });
});

test("validação local e controle de visibilidade da senha", async ({
  page,
}) => {
  await page.goto("/login");
  await page.getByRole("button", { name: "Acessar plataforma" }).click();
  await expect(page.getByText("Informe um e-mail válido.")).toBeVisible();
  await expect(page.getByText("Informe sua senha.")).toBeVisible();
  await page.getByLabel("Senha", { exact: true }).fill("senha sintética");
  await page.getByRole("button", { name: "Mostrar senha" }).click();
  await expect(page.getByLabel("Senha", { exact: true })).toHaveAttribute(
    "type",
    "text",
  );
  await page.getByRole("button", { name: "Ocultar senha" }).click();
  await expect(page.getByLabel("Senha", { exact: true })).toHaveAttribute(
    "type",
    "password",
  );
});

test("erro de integração não autentica nem redireciona", async ({ page }) => {
  await page.route("**/api/v1/auth/login", (route) =>
    route.fulfill({ status: 503, json: { detail: "indisponível" } }),
  );
  await page.goto("/login");
  await page
    .getByRole("textbox", { name: "E-mail" })
    .fill("teste@example.invalid");
  await page.getByLabel("Senha", { exact: true }).fill("synthetic-only");
  await page.getByRole("button", { name: "Acessar plataforma" }).click();
  await expect(
    page
      .getByRole("region", { name: "Entrar na plataforma" })
      .getByRole("alert"),
  ).toContainText("indisponível");
  await expect(page).toHaveURL(/\/login$/);
  expect(await page.evaluate(() => localStorage.length)).toBe(0);
});

test("cadastros e área técnica exigem sessão no servidor", async ({ page }) => {
  for (const route of ["/cadastros", "/analises", "/tecnologia/conexao"]) {
    await page.goto(route);
    await expect(page).toHaveURL(/\/login$/);
    await expect(
      page.getByRole("heading", { name: "Entrar na plataforma" }),
    ).toBeVisible();
  }
});

test("proxy recusa origem externa e rotas não autorizadas", async ({
  request,
}) => {
  const origin = await request.post("/api/v1/auth/login", {
    headers: { Origin: "https://evil.invalid" },
    data: {},
  });
  expect(origin.status()).toBe(403);
  const forbidden = await request.get("/api/v1/arbitrary-query");
  expect(forbidden.status()).toBe(404);
  expect(forbidden.headers()["cache-control"]).toContain("no-store");
});

test("WhatsApp usa apenas telefone normalizado e atendimento usa fuso institucional", () => {
  expect(whatsappContact("+5583999991111")).toEqual({
    url: "https://wa.me/5583999991111",
    label: "(83) 99999-1111",
  });
  for (const invalid of [
    null,
    "MARIA · +55 (83) 99999-1111",
    "+5500999991111",
    "javascript:alert(1)",
    "+558312341234",
  ]) {
    expect(whatsappContact(invalid)).toBeNull();
  }
  expect(formatLastAppointment(null)).toBe("Sem atendimentos");
  expect(formatLastAppointment("2026-10-21T15:30:00Z")).toContain("12:30");
});

test("cadastros vazios e modal seguem permissões e teclado", async ({
  page,
  context,
}, info) => {
  await context.addCookies([
    {
      name: "ac_social_ss",
      value: "fixture-social",
      url: "http://localhost:3000",
    },
  ]);
  await page.goto("/cadastros");
  await expect(
    page.getByRole("heading", { name: "Nenhum cadastro encontrado" }),
  ).toBeVisible();
  await expect(page.getByRole("table")).toHaveCount(0);
  await expect(
    page.getByRole("link", { name: "Status da conexão" }),
  ).toHaveCount(0);
  if (info.project.name === "mobile")
    await page.getByRole("button", { name: "Expandir menu" }).click();
  await expect(
    page.getByRole("link", { name: "Agenda Digital (abre em nova aba)" }),
  ).toHaveAttribute("href", "https://agenda-digital-ac-social.vercel.app");
  if (info.project.name === "mobile")
    await page.getByRole("button", { name: "Recolher menu" }).click();
  await expect
    .poll(async () => {
      const sidebar = await page.locator(".sidebar").boundingBox();
      const main = await page.locator(".app-main").boundingBox();
      return main!.x >= sidebar!.x + sidebar!.width - 1;
    })
    .toBe(true);
  await page.screenshot({
    path: `output/screenshots/cadastros-${info.project.name}.png`,
    fullPage: true,
    animations: "disabled",
  });
  await page.getByRole("button", { name: "Novo cadastro" }).first().click();
  await expect(page.getByRole("dialog")).toContainText(
    "Identificação do usuário",
  );
  const audit = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(audit.violations).toEqual([]);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("Tecnologia tem diagnóstico e não recebe permissões sociais implícitas", async ({
  page,
  context,
}, info) => {
  await context.addCookies([
    {
      name: "ac_social_ss",
      value: "fixture-technology",
      url: "http://localhost:3000",
    },
  ]);
  await page.goto("/tecnologia/conexao");
  await expect(
    page.getByRole("heading", { name: "Status da conexão" }),
  ).toBeVisible();
  await expect(
    page.getByText("Banco institucional", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Análise de dados" }),
  ).toHaveCount(0);
  await page.screenshot({
    path: `output/screenshots/tecnologia-${info.project.name}.png`,
    fullPage: true,
    animations: "disabled",
  });
  const audit = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(audit.violations).toEqual([]);
});

test("rota técnica bloqueia também navegação direta de outra equipe", async ({
  page,
  context,
}) => {
  await context.addCookies([
    {
      name: "ac_social_ss",
      value: "fixture-social",
      url: "http://localhost:3000",
    },
  ]);
  await page.goto("/tecnologia/conexao");
  await expect(
    page.getByRole("heading", { name: "Página não encontrada" }),
  ).toBeVisible();
  await expect(
    page.getByText("Banco institucional", { exact: true }),
  ).toHaveCount(0);
});

test("menu móvel mantém foco e fecha por Escape", async ({
  page,
  context,
}, info) => {
  test.skip(info.project.name !== "mobile");
  await context.addCookies([
    {
      name: "ac_social_ss",
      value: "fixture-social",
      url: "http://localhost:3000",
    },
  ]);
  await page.goto("/cadastros");
  await page.getByRole("button", { name: "Expandir menu" }).click();
  await expect(
    page.getByRole("dialog", { name: "Menu principal" }),
  ).toBeVisible();
  for (let index = 0; index < 8; index++) {
    await page.keyboard.press("Tab");
    expect(
      await page.evaluate(() =>
        document.querySelector(".sidebar")?.contains(document.activeElement),
      ),
    ).toBe(true);
  }
  await page.keyboard.press("Escape");
  await expect(
    page.getByRole("button", { name: "Expandir menu" }),
  ).toBeVisible();
});
