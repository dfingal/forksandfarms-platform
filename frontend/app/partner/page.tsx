import type { Metadata } from "next";
import PartnerHero from "@/components/partner/PartnerHero";
import WhyForksAndFarms from "@/components/partner/WhyForksAndFarms";
import WhyVenuesPartner from "@/components/partner/WhyVenuesPartner";
import PartnerProof from "@/components/partner/PartnerProof";
import PartnershipOptions from "@/components/partner/PartnershipOptions";
import HowItWorks from "@/components/partner/HowItWorks";
import PartnerFAQ from "@/components/partner/PartnerFAQ";
import PartnerApplicationForm from "@/components/partner/PartnerApplicationForm";

export const metadata: Metadata = {
  title: "Partner With Us · Forks And Farms",
  description: "Plants that pay their way — partner your St. Louis venue with Forks And Farms.",
};

// Page order per spec §3.4.
export default function PartnerPage() {
  return (
    <div>
      <PartnerHero />
      <WhyForksAndFarms />
      <WhyVenuesPartner />
      <PartnerProof />
      <PartnershipOptions />
      <HowItWorks />
      <PartnerFAQ />
      <PartnerApplicationForm />
    </div>
  );
}
