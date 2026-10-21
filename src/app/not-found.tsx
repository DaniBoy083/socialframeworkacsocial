import Link from "next/link";
export default function NotFound() {
  return (
    <main id="conteudo" className="error-panel">
      <h1>Página não encontrada</h1>
      <p>Confira o endereço ou retorne à plataforma.</p>
      <Link href="/cadastros">Voltar à plataforma</Link>
    </main>
  );
}
