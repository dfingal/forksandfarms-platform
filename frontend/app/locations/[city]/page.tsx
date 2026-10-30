import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getCities, getCity } from "@/lib/api";
import VenueCardGrid from "@/components/VenueCardGrid";
import PartnerCallout from "@/components/PartnerCallout";

// Prerender every known city at build time...
export async function generateStaticParams() {
  const cities = await getCities();
  return (cities ?? []).map((city) => ({ city: city.slug }));
}

// ...but a city added after the last build (or one whose is_active flips
// to true) still renders correctly on first visit instead of 404ing —
// dynamicParams defaults to true, this just makes that explicit.
export const dynamicParams = true;
export const revalidate = 600; // 10 minutes, matches the rest of the site

interface PageProps {
  params: Promise<{ city: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { city: citySlug } = await params;
  const city = await getCity(citySlug);
  if (!city) return {};

  return {
    title: `Forks And Farms in ${city.name}`,
    description: city.intro || `Find Forks And Farms plant locations in ${city.name}.`,
  };
}

export default async function CityLocationsPage({ params }: PageProps) {
  const { city: citySlug } = await params;
  const city = await getCity(citySlug);

  // Covers both an unknown slug and a city with is_active=false — the API
  // 404s both identically, so there's nothing to distinguish here.
  if (!city) {
    notFound();
  }

  return (
    <div>
      <div className="mx-auto max-w-6xl px-4 py-7 sm:px-6">
        <h1 className="text-forest">Forks And Farms in {city.name}</h1>
        {city.intro && <p className="mt-2 max-w-xl text-forest/80">{city.intro}</p>}

        <div className="mt-6">
          <VenueCardGrid venues={city.venues} />
        </div>
      </div>

      <PartnerCallout />
    </div>
  );
}
