import { afterEach, describe, expect, it, vi } from "vitest";
import { buildMetadata, DEFAULT_SHARE_IMAGE, getSiteUrl, type MetadataFallback } from "./seo";
import type { SeoMeta } from "./types";

const SITE = new URL("https://forksandfarms.example");

const FALLBACK: MetadataFallback = {
  title: "Plants at Northwest Coffee · Forks And Farms",
  description: "Ferns by the espresso bar.",
  path: "/locations/st-louis/northwest-coffee",
};

const SEO: SeoMeta = {
  title: "Custom title · Forks And Farms",
  description: "Custom description.",
  og_image: "https://res.cloudinary.com/demo/image/upload/share.jpg",
  canonical_url: null,
  noindex: false,
};

describe("buildMetadata with a missing seo object (backend not deployed yet)", () => {
  it.each([undefined, null])("falls back to the page's own values when seo is %s", (seo) => {
    const metadata = buildMetadata(seo, FALLBACK, SITE);

    expect(metadata.title).toBe(FALLBACK.title);
    expect(metadata.description).toBe(FALLBACK.description);
    expect(metadata.openGraph?.images).toEqual([DEFAULT_SHARE_IMAGE]);
    expect(metadata.twitter).toMatchObject({ card: "summary_large_image", images: [DEFAULT_SHARE_IMAGE.url] });
    expect(metadata.alternates?.canonical).toBe(FALLBACK.path);
    expect(metadata.robots).toBeUndefined();
  });

  it("doesn't throw on a partially-filled seo object", () => {
    const partial = { title: "", description: "" } as unknown as SeoMeta;
    const metadata = buildMetadata(partial, FALLBACK, SITE);
    expect(metadata.title).toBe(FALLBACK.title);
    expect(metadata.description).toBe(FALLBACK.description);
  });
});

describe("buildMetadata with a seo object", () => {
  it("uses the seo title, description and share image", () => {
    const metadata = buildMetadata(SEO, FALLBACK, SITE);

    expect(metadata.title).toBe(SEO.title);
    expect(metadata.description).toBe(SEO.description);
    expect(metadata.openGraph).toMatchObject({
      title: SEO.title,
      description: SEO.description,
      siteName: "Forks And Farms",
      images: [{ url: SEO.og_image }],
    });
    expect(metadata.twitter).toMatchObject({ title: SEO.title, images: [SEO.og_image] });
  });

  it("uses the default share image when og_image is null", () => {
    const metadata = buildMetadata({ ...SEO, og_image: null }, FALLBACK, SITE);
    expect(metadata.openGraph?.images).toEqual([DEFAULT_SHARE_IMAGE]);
  });

  it("sets robots noindex (but still follow) when noindex is true", () => {
    expect(buildMetadata({ ...SEO, noindex: true }, FALLBACK, SITE).robots).toEqual({
      index: false,
      follow: true,
    });
  });

  it("leaves robots alone when noindex is false", () => {
    expect(buildMetadata(SEO, FALLBACK, SITE).robots).toBeUndefined();
  });
});

describe("canonical URL", () => {
  it("defaults to the page path when the site URL is known", () => {
    const metadata = buildMetadata(SEO, FALLBACK, SITE);
    expect(metadata.alternates?.canonical).toBe(FALLBACK.path);
    expect(metadata.openGraph).toMatchObject({ url: FALLBACK.path });
  });

  it("uses the admin override when set, even without a site URL", () => {
    const override = "https://example.com/elsewhere";
    for (const site of [SITE, undefined]) {
      expect(buildMetadata({ ...SEO, canonical_url: override }, FALLBACK, site).alternates?.canonical).toBe(
        override
      );
    }
  });

  it("is omitted when there's no override and no site URL (never point at localhost)", () => {
    const metadata = buildMetadata(SEO, FALLBACK, undefined);
    expect(metadata.alternates).toBeUndefined();
    expect(metadata.openGraph).not.toHaveProperty("url");
  });
});

describe("getSiteUrl", () => {
  afterEach(() => vi.restoreAllMocks());

  it("parses a valid URL", () => {
    expect(getSiteUrl("https://forksandfarms.example")?.origin).toBe("https://forksandfarms.example");
  });

  it("returns undefined when unset", () => {
    expect(getSiteUrl("")).toBeUndefined();
    expect(getSiteUrl(undefined)).toBeUndefined();
  });

  it("returns undefined (with a warning) for an invalid value", () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    expect(getSiteUrl("forksandfarms.example")).toBeUndefined();
    expect(warn).toHaveBeenCalled();
  });
});
