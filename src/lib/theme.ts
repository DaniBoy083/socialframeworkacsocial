"use client";
import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    primary: { main: "#d90f30", dark: "#b80d27", contrastText: "#ffffff" },
    secondary: { main: "#65111f" },
    background: { default: "#fff8f9", paper: "#ffffff" },
    text: { primary: "#65111f", secondary: "#6f2a36" },
    divider: "#ef163624",
  },
  typography: {
    fontFamily: "Arial, Helvetica, sans-serif",
    h1: { fontSize: "2rem", fontWeight: 800 },
    h2: { fontSize: "1.45rem", fontWeight: 750 },
    button: { textTransform: "none", fontWeight: 700 },
  },
  shape: { borderRadius: 14 },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: { root: { minHeight: 46 } },
    },
    MuiTextField: { defaultProps: { fullWidth: true, variant: "outlined" } },
    MuiOutlinedInput: {
      styleOverrides: { root: { backgroundColor: "#fff8f9" } },
    },
    MuiDialog: { defaultProps: { fullWidth: true, maxWidth: "md" } },
    MuiCssBaseline: {
      styleOverrides: {
        "*:focus-visible": { outline: "3px solid #65111f", outlineOffset: 3 },
      },
    },
  },
});
