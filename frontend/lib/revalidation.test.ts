import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { isAllowedPath, MAX_PATHS, parsePaths, SECRET_HEADER, secretMatches } from "./revalidation";

// The route calls next/cache's revalidatePath, which only works inside a
// running Next.js server — replace it with a spy for these tests.
vi.mock("next/cache", () => ({ revalidatePath: vi.fn() }));
import { revalidatePath } from "next/cache";
import { POST } from "@/app/api/revalidate/route";

describe("isAllowedPath", () => {
  it.each(["/", "/partner", "/locations/st-louis", "/locations/st-louis/northwest-coffee", "/locations/a_b/C-1"])(
    "allows %s",
    (path) => expect(isAllowedPath(path)).toBe(true)
  );

  it.each([
    "",
    "/locations",
    "/locations/",
    "/partner/thanks",
    "/locations/st-louis/venue/extra",
    "/locations/st louis",
    "/locations/../admin",
    "https://evil.example/",
    "//evil.example",
    "/api/revalidate",
    42,
    null,
  ])("rejects %j", (path) => expect(isAllowedPath(path)).toBe(false));
});

describe("parsePaths", () => {
  it("accepts a valid list and drops duplicates", () => {
    expect(parsePaths({ paths: ["/", "/partner", "/"] })).toEqual({ ok: true, paths: ["/", "/partner"] });
  });

  it.each([null, "x", {}, { paths: "/" }, { paths: [] }])("rejects malformed body %j", (body) => {
    expect(parsePaths(body).ok).toBe(false);
  });

  it("rejects the whole request if any path is invalid", () => {
    const result = parsePaths({ paths: ["/", "/admin"] });
    expect(result).toEqual({ ok: false, error: expect.stringContaining("/admin") });
  });

  it("rejects too many paths", () => {
    const paths = Array.from({ length: MAX_PATHS + 1 }, (_, i) => `/locations/city-${i}`);
    expect(parsePaths({ paths }).ok).toBe(false);
  });
});

describe("secretMatches", () => {
  it("matches only the exact secret", () => {
    expect(secretMatches("s3cret", "s3cret")).toBe(true);
    expect(secretMatches("s3cre", "s3cret")).toBe(false);
    expect(secretMatches("s3cret-and-more", "s3cret")).toBe(false);
  });

  it("never matches when either side is missing", () => {
    expect(secretMatches(null, "s3cret")).toBe(false);
    expect(secretMatches("", "s3cret")).toBe(false);
    expect(secretMatches("", "")).toBe(false);
  });
});

describe("POST /api/revalidate", () => {
  const SECRET = "test-secret";

  function post(body: unknown, secret: string | null = SECRET) {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (secret !== null) headers[SECRET_HEADER] = secret;
    return POST(
      new Request("http://localhost/api/revalidate", {
        method: "POST",
        headers,
        body: typeof body === "string" ? body : JSON.stringify(body),
      })
    );
  }

  beforeEach(() => {
    vi.stubEnv("REVALIDATE_SECRET", SECRET);
    vi.mocked(revalidatePath).mockClear();
    vi.spyOn(console, "error").mockImplementation(() => {});
  });
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it("revalidates each valid path", async () => {
    const response = await post({ paths: ["/", "/locations/st-louis/northwest-coffee"] });
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ revalidated: ["/", "/locations/st-louis/northwest-coffee"] });
    expect(revalidatePath).toHaveBeenCalledTimes(2);
    expect(revalidatePath).toHaveBeenCalledWith("/locations/st-louis/northwest-coffee");
  });

  it("401s on a wrong or missing secret, revalidating nothing", async () => {
    expect((await post({ paths: ["/"] }, "wrong")).status).toBe(401);
    expect((await post({ paths: ["/"] }, null)).status).toBe(401);
    expect(revalidatePath).not.toHaveBeenCalled();
  });

  it("400s on an invalid path or bad JSON, revalidating nothing", async () => {
    expect((await post({ paths: ["/", "/admin"] })).status).toBe(400);
    expect((await post("not json")).status).toBe(400);
    expect(revalidatePath).not.toHaveBeenCalled();
  });

  it("500s if REVALIDATE_SECRET isn't set on the server", async () => {
    vi.stubEnv("REVALIDATE_SECRET", "");
    expect((await post({ paths: ["/"] }, "")).status).toBe(500);
    expect(revalidatePath).not.toHaveBeenCalled();
  });
});
