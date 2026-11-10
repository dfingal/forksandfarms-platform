/**
 * Checks for the on-demand revalidation endpoint (app/api/revalidate/route.ts).
 *
 * Kept as small pure functions, separate from the route, so they can be
 * unit-tested with vitest without running Next.js.
 *
 * The Django side (backend/core/revalidation.py) sends:
 *   POST /api/revalidate
 *   X-Revalidate-Secret: <REVALIDATE_SECRET>
 *   { "paths": ["/", "/locations/st-louis", ...] }
 */

import { createHash, timingSafeEqual } from "node:crypto";

/** Header name — must match SECRET_HEADER in backend/core/revalidation.py. */
export const SECRET_HEADER = "x-revalidate-secret";

/** A city with many venues still fits comfortably; anything bigger is suspicious. */
export const MAX_PATHS = 100;

// Django SlugField allows letters, numbers, hyphens and underscores.
const SLUG = "[A-Za-z0-9_-]+";

/** The only pages Django is allowed to ask us to refresh. */
const ALLOWED_PATH_PATTERNS = [
  /^\/$/,
  /^\/partner$/,
  new RegExp(`^/locations/${SLUG}$`),
  new RegExp(`^/locations/${SLUG}/${SLUG}$`),
];

export function isAllowedPath(path: unknown): path is string {
  return typeof path === "string" && ALLOWED_PATH_PATTERNS.some((pattern) => pattern.test(path));
}

export type ParsePathsResult = { ok: true; paths: string[] } | { ok: false; error: string };

/** Validate a request body of the form `{ "paths": [...] }`. All-or-nothing:
 * one bad path rejects the whole request, so a typo is noticed rather
 * than half-applied. Duplicates are dropped. */
export function parsePaths(body: unknown): ParsePathsResult {
  if (typeof body !== "object" || body === null || !("paths" in body)) {
    return { ok: false, error: 'Body must be JSON like { "paths": ["/"] }.' };
  }
  const { paths } = body as { paths: unknown };
  if (!Array.isArray(paths) || paths.length === 0) {
    return { ok: false, error: '"paths" must be a non-empty list.' };
  }
  if (paths.length > MAX_PATHS) {
    return { ok: false, error: `Too many paths (max ${MAX_PATHS}).` };
  }
  const invalid = paths.filter((path) => !isAllowedPath(path));
  if (invalid.length > 0) {
    return { ok: false, error: `Not an allowed path: ${JSON.stringify(invalid)}` };
  }
  return { ok: true, paths: [...new Set(paths as string[])] };
}

/** Compare the request's secret to ours in constant time (so response
 * timing can't leak how much of a guess was right). Hashing first makes
 * both sides the same length, which timingSafeEqual requires. */
export function secretMatches(provided: string | null, expected: string): boolean {
  if (!provided || !expected) return false;
  const digest = (value: string) => createHash("sha256").update(value).digest();
  return timingSafeEqual(digest(provided), digest(expected));
}
