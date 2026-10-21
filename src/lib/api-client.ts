"use client";
import axios from "axios";
export const api = axios.create({
  baseURL: "/api/v1",
  timeout: 15000,
  withCredentials: true,
});
export function apiMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const messages: Record<number, string> = {
      401: "Credenciais ou sessão inválidas. Entre novamente.",
      403: "Você não tem permissão para este acesso.",
      413: "A requisição excede o limite permitido.",
      422: "Verifique os campos informados.",
      429: "Muitas tentativas. Aguarde 15 minutos antes de tentar novamente.",
      503: "A integração institucional está indisponível. Fale com a equipe de Tecnologia.",
    };
    return (
      messages[error.response?.status ?? 0] ??
      "Não foi possível concluir a operação. Tente novamente."
    );
  }
  return "Não foi possível concluir a operação. Tente novamente.";
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && error.config?.url !== "/auth/login") {
      window.dispatchEvent(new Event("institutional-session-expired"));
    }
    return Promise.reject(error);
  },
);
