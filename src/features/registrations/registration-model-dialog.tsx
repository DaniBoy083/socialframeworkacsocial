"use client";
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  useMediaQuery,
  useTheme,
} from "@mui/material";

export function RegistrationModelDialog({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const fullScreen = useMediaQuery(useTheme().breakpoints.down("sm"));
  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullScreen={fullScreen}
      aria-labelledby="registration-model-title"
    >
      <DialogTitle id="registration-model-title">Novo cadastro</DialogTitle>
      <DialogContent>
        <Alert severity="info">
          O cadastro será liberado após a validação da integração e das
          permissões institucionais.
        </Alert>
        <p>A ficha seguirá o Cadastro Social Unificado da AC Social:</p>
        <ol>
          <li>Identificação do usuário</li>
          <li>Contato e endereço</li>
          <li>Situação socioeconômica</li>
          <li>Composição familiar</li>
          <li>Parecer técnico</li>
        </ol>
        <p>
          A ciência cadastral e a autorização de uso de imagem terão registros
          separados, conforme a versão institucional aprovada do termo.
        </p>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Fechar</Button>
      </DialogActions>
    </Dialog>
  );
}
