import { redirect } from "next/navigation";

// Phase I has one city; spec §3 says /locations redirects to
// /locations/st-louis until a second city exists (then this becomes a
// real city picker).
export default function LocationsIndex() {
  redirect("/locations/st-louis");
}
