"use client";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import { formatLastAppointment, whatsappContact } from "./formatters";

export interface Registration {
  id: string;
  name: string;
  lastAppointmentAt: string | null;
  phone: string | null;
}
// Transport/action integration is intentionally absent until the social contract is approved.
export function RegistrationTable({ items }: { items: Registration[] }) {
  if (!items.length) return null;
  return (
    <TableContainer sx={{ mt: 3 }}>
      <Table aria-label="Cadastros do Serviço Social" sx={{ minWidth: 640 }}>
        <TableHead>
          <TableRow>
            {[
              "Nome do usuário",
              "Data e horário do último atendimento",
              "WhatsApp",
              "Ações",
            ].map((label) => (
              <TableCell key={label} sx={{ fontWeight: 700 }}>
                {label}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {items.map((item) => {
            const contact = whatsappContact(item.phone);
            return (
              <TableRow key={item.id}>
                <TableCell component="th" scope="row">
                  {item.name}
                </TableCell>
                <TableCell>
                  {formatLastAppointment(item.lastAppointmentAt)}
                </TableCell>
                <TableCell>
                  {contact ? (
                    <a
                      href={contact.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={`WhatsApp de ${item.name} (abre em nova aba)`}
                    >
                      {contact.label} ↗
                    </a>
                  ) : (
                    "Sem contato"
                  )}
                </TableCell>
                <TableCell>Operações em preparação</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
