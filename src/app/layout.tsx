import type { Metadata } from "next";
import { Providers } from "./providers";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Social Framework | AC Social",
    template: "%s | AC Social",
  },
  description: "Ambiente institucional do Serviço Social da AC Social.",
  robots: { index: false, follow: false },
  icons: { icon: "/brand/ac-social.png" },
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>
        <Providers>
          <a className="skip-link" href="#conteudo">
            Pular para o conteúdo
          </a>
          <div className="page-body">{children}</div>
          <footer className="institutional-footer">
            <div>
              <strong>AC SOCIAL | SOCIAL FRAMEWORK</strong>
              <span>
                Ambiente institucional para o atendimento do Serviço Social.
              </span>
            </div>
          </footer>
        </Providers>
      </body>
    </html>
  );
}
