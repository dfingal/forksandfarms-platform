import type { Metadata } from "next";
import ThanksContent from "@/components/partner/ThanksContent";

export const metadata: Metadata = {
  title: "Application received · Forks And Farms",
  description: "Thanks for applying to partner with Forks And Farms.",
};

export default function PartnerThanksPage() {
  return <ThanksContent />;
}
