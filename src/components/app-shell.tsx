"use client";
import { useEffect, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import FocusTrap from "@mui/material/Unstable_TrapFocus";
import { usePathname, useRouter } from "next/navigation";
import { Alert, Button, IconButton, Tooltip } from "@mui/material";
import {
  FiArrowUpRight,
  FiBarChart2,
  FiChevronRight,
  FiDatabase,
  FiLogOut,
  FiMenu,
  FiUsers,
  FiX,
} from "react-icons/fi";
import { useQueryClient } from "@tanstack/react-query";
import { api, apiMessage } from "@/src/lib/api-client";
import type { Actor } from "@/src/features/auth/types";

const subscribe = (callback: () => void) => {
  const media = window.matchMedia("(max-width: 599px)");
  media.addEventListener("change", callback);
  return () => media.removeEventListener("change", callback);
};
export function AppShell({
  actor,
  children,
}: {
  actor: Actor;
  children: React.ReactNode;
}) {
  const mobile = useSyncExternalStore(
    subscribe,
    () => window.matchMedia("(max-width: 599px)").matches,
    () => false,
  );
  const [expanded, setExpanded] = useState<boolean | null>(null);
  const collapsed = expanded === null ? mobile : !expanded;
  const [logoutError, setLogoutError] = useState("");
  const [leaving, setLeaving] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const queries = useQueryClient();
  useEffect(() => {
    const expired = () => {
      queries.clear();
      router.replace("/login");
      router.refresh();
    };
    window.addEventListener("institutional-session-expired", expired);
    return () =>
      window.removeEventListener("institutional-session-expired", expired);
  }, [queries, router]);
  const links = [
    { href: "/cadastros", label: "Cadastros", icon: FiUsers, visible: true },
    {
      href: "/analises",
      label: "Análise de dados",
      icon: FiBarChart2,
      visible: actor.permissions.includes("analytics:read"),
    },
    {
      href: "/tecnologia/conexao",
      label: "Status da conexão",
      icon: FiDatabase,
      visible: actor.isTechnology,
    },
  ].filter((link) => link.visible);
  async function logout() {
    setLeaving(true);
    setLogoutError("");
    try {
      await api.post("/auth/logout");
      queries.clear();
      router.replace("/login");
      router.refresh();
    } catch (failure) {
      setLogoutError(apiMessage(failure));
      setLeaving(false);
    }
  }
  return (
    <div className={`app-shell ${collapsed ? "is-collapsed" : ""}`}>
      <FocusTrap open={mobile && !collapsed}>
        <aside
          className="sidebar"
          aria-label="Menu principal"
          role={mobile && !collapsed ? "dialog" : undefined}
          aria-modal={mobile && !collapsed ? true : undefined}
          onKeyDown={(event) => {
            if (event.key === "Escape" && mobile) setExpanded(false);
          }}
        >
          <div className="sidebar-heading">
            {!collapsed && <strong>Menu</strong>}
            <IconButton
              sx={{ color: "white" }}
              aria-label={collapsed ? "Expandir menu" : "Recolher menu"}
              aria-expanded={!collapsed}
              aria-controls="system-navigation"
              onClick={() => setExpanded(collapsed)}
            >
              {collapsed ? <FiMenu /> : <FiX />}
            </IconButton>
          </div>
          <nav
            className="sidebar-nav"
            id="system-navigation"
            aria-label="Módulos do sistema"
          >
            {!collapsed && <p className="sidebar-label">Módulos do sistema</p>}
            {links.map(({ href, label, icon: Icon }) => (
              <Tooltip
                key={href}
                title={collapsed ? label : ""}
                placement="right"
              >
                <Link
                  className="sidebar-link"
                  href={href}
                  aria-label={collapsed ? label : undefined}
                  aria-current={pathname === href ? "page" : undefined}
                  onClick={() => {
                    if (mobile) setExpanded(false);
                  }}
                >
                  <Icon aria-hidden />
                  {!collapsed && (
                    <>
                      {label}
                      <FiChevronRight className="link-arrow" aria-hidden />
                    </>
                  )}
                </Link>
              </Tooltip>
            ))}
          </nav>
          <div className="sidebar-bottom">
            {!collapsed && (
              <div className="session-card">
                <strong>Sessão ativa</strong>
                <span>{actor.name}</span>
                <span>{actor.teams.join(" · ")}</span>
              </div>
            )}
            <Tooltip
              title={collapsed ? "Agenda Digital (abre em nova aba)" : ""}
              placement="right"
            >
              <a
                className="sidebar-link"
                href="https://agenda-digital-ac-social.vercel.app"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Agenda Digital (abre em nova aba)"
              >
                <FiArrowUpRight aria-hidden />
                {!collapsed && "Agenda Digital"}
              </a>
            </Tooltip>
            {logoutError && (
              <Alert severity="error" sx={{ mb: 1 }}>
                {logoutError}
              </Alert>
            )}
            <Button
              fullWidth
              variant="contained"
              onClick={logout}
              disabled={leaving}
              aria-label="Sair da plataforma"
              startIcon={!collapsed ? <FiLogOut /> : undefined}
              sx={{ background: "#d90f30", minWidth: 0 }}
            >
              {collapsed ? <FiLogOut /> : leaving ? "Saindo…" : "Sair"}
            </Button>
          </div>
        </aside>
      </FocusTrap>
      <main
        inert={mobile && !collapsed}
        className="app-main"
        id="conteudo"
        tabIndex={-1}
      >
        <div className="content-stack">{children}</div>
      </main>
    </div>
  );
}
