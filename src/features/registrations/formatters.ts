export function formatLastAppointment(value: string | null): string {
  if (!value) return "Sem atendimentos";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Sem atendimentos";
  return new Intl.DateTimeFormat("pt-BR", {
    timeZone: "America/Fortaleza",
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}
export function whatsappContact(
  value: string | null,
): { url: string; label: string } | null {
  // Accept only an explicit, normalized Brazilian telephone, never free-text responsible_contact.
  if (!value || !/^\+55[1-9]\d9\d{8}$/.test(value)) return null;
  const number = value.slice(3);
  const ddd = number.slice(0, 2);
  const areaCodes = new Set([
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "21",
    "22",
    "24",
    "27",
    "28",
    "31",
    "32",
    "33",
    "34",
    "35",
    "37",
    "38",
    "41",
    "42",
    "43",
    "44",
    "45",
    "46",
    "47",
    "48",
    "49",
    "51",
    "53",
    "54",
    "55",
    "61",
    "62",
    "63",
    "64",
    "65",
    "66",
    "67",
    "68",
    "69",
    "71",
    "73",
    "74",
    "75",
    "77",
    "79",
    "81",
    "82",
    "83",
    "84",
    "85",
    "86",
    "87",
    "88",
    "89",
    "91",
    "92",
    "93",
    "94",
    "95",
    "96",
    "97",
    "98",
    "99",
  ]);
  if (!areaCodes.has(ddd)) return null;
  return {
    url: `https://wa.me/${value.slice(1)}`,
    label: `(${ddd}) ${number.slice(2, 7)}-${number.slice(7)}`,
  };
}
