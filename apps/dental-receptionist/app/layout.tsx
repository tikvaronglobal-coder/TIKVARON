import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "TIKVARON Dental Receptionist",
  description: "A staging demonstration of a helpful, human-centred dental receptionist."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}