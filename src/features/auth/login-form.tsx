"use client";
import { useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import {
  Alert,
  Button,
  IconButton,
  InputAdornment,
  TextField,
} from "@mui/material";
import { FiEye, FiEyeOff, FiLock, FiMail, FiShield } from "react-icons/fi";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQueryClient } from "@tanstack/react-query";
import { api, apiMessage } from "@/src/lib/api-client";

const schema = z.object({
  email: z.string().trim().email("Informe um e-mail válido.").max(254),
  password: z
    .string()
    .min(1, "Informe sua senha.")
    .max(512, "A senha excede o tamanho permitido."),
});
type Input = z.infer<typeof schema>;
export function LoginForm({ unavailable = false }: { unavailable?: boolean }) {
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();
  const queries = useQueryClient();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Input>({ resolver: zodResolver(schema) });
  const submit = handleSubmit(async (values) => {
    setError("");
    try {
      await api.post("/auth/login", values);
      const session = await api.get("/auth/session");
      if (!session.data.authenticated) throw new Error("session");
      queries.clear();
      router.replace("/cadastros");
      router.refresh();
    } catch (failure) {
      setError(apiMessage(failure));
    }
  });
  return (
    <main id="conteudo" className="login-page">
      <p className="eyebrow login-eyebrow">
        Acesso institucional | Social Framework
      </p>
      <section className="login-card" aria-labelledby="login-title">
        <div className="brand-logo">
          <Image
            className="brand-source"
            src="/brand/ac-social.png"
            alt="AC Social"
            width={208}
            height={208}
            priority
            unoptimized
          />
        </div>
        <h1 id="login-title">Entrar na plataforma</h1>
        <p className="login-description">
          Use seu e-mail institucional e sua senha para continuar.
        </p>
        {(error || unavailable) && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error ||
              "A integração institucional está indisponível. Fale com a equipe de Tecnologia."}
          </Alert>
        )}
        <form className="login-form" onSubmit={submit} noValidate>
          <TextField
            label="E-mail"
            type="email"
            autoComplete="username"
            placeholder="seunome@acsocial.org.br"
            {...register("email")}
            error={!!errors.email}
            helperText={errors.email?.message}
            slotProps={{
              input: {
                startAdornment: (
                  <InputAdornment position="start">
                    <FiMail aria-hidden />
                  </InputAdornment>
                ),
              },
            }}
          />
          <TextField
            label="Senha"
            type={show ? "text" : "password"}
            autoComplete="current-password"
            placeholder="Digite sua senha"
            {...register("password")}
            error={!!errors.password}
            helperText={errors.password?.message}
            slotProps={{
              input: {
                startAdornment: (
                  <InputAdornment position="start">
                    <FiLock aria-hidden />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label={show ? "Ocultar senha" : "Mostrar senha"}
                      onClick={() => setShow(!show)}
                      edge="end"
                    >
                      {show ? <FiEyeOff /> : <FiEye />}
                    </IconButton>
                  </InputAdornment>
                ),
              },
            }}
          />
          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={isSubmitting}
            sx={{ minHeight: 52 }}
          >
            {isSubmitting ? "Verificando acesso…" : "Acessar plataforma"}
          </Button>
        </form>
        <aside className="login-support">
          <strong>
            <FiShield aria-hidden /> Suporte de acesso
          </strong>
          <p>
            Precisa de suporte? Fale com a equipe administrativa da AC Social
            para liberar ou atualizar seu acesso.
          </p>
        </aside>
      </section>
    </main>
  );
}
