/**
 * POST /api/revalidate — on-demand page refresh, called by Django when a
 * City/Venue (or its photos/hours) is saved or deleted in admin
 * (backend/core/revalidation.py; spec §7).
 *
 * Protected by a shared secret in the X-Revalidate-Secret header and
 * only accepts known page paths (lib/revalidation.ts). Each path is
 * marked stale and rebuilt on its next visit; the 10-minute
 * time-based revalidation on every page stays as the fallback.
 */

import { revalidatePath } from "next/cache";
import { parsePaths, SECRET_HEADER, secretMatches } from "@/lib/revalidation";

export async function POST(request: Request) {
  const expectedSecret = process.env.REVALIDATE_SECRET;
  if (!expectedSecret) {
    console.error("REVALIDATE_SECRET is not set — /api/revalidate is disabled.");
    return Response.json({ error: "Revalidation is not configured." }, { status: 500 });
  }

  if (!secretMatches(request.headers.get(SECRET_HEADER), expectedSecret)) {
    return Response.json({ error: "Invalid secret." }, { status: 401 });
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "Body must be valid JSON." }, { status: 400 });
  }

  const result = parsePaths(body);
  if (!result.ok) {
    return Response.json({ error: result.error }, { status: 400 });
  }

  for (const path of result.paths) {
    revalidatePath(path);
  }
  return Response.json({ revalidated: result.paths });
}
