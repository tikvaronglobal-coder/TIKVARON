import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "TIKVARON Sales Growth",
  description: "TIKVARON's private HubSpot integration and sales operations preview."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}