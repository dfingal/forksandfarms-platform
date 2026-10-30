import type { CityDetail } from "@/lib/types";
import VenueMap from "./VenueMap";

// scroll-mt-24 offsets the #map anchor so "Find Plants Near You" doesn't
// land the heading underneath the sticky header.
export default function MapSection({ city }: { city: CityDetail }) {
  return (
    <section id="map" className="scroll-mt-24 mx-auto max-w-6xl px-4 py-7 sm:px-6">
      <h2 className="mb-3 text-forest">Find plants near you</h2>
      <VenueMap city={city} venues={city.venues} />
    </section>
  );
}
