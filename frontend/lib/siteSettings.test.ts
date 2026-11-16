import { describe, expect, it } from "vitest";
import { isOptimizableImage, NO_SITE_IMAGES, parseSiteImage, parseSiteImages } from "./siteSettings";

const CLOUDINARY = "https://res.cloudinary.com/demo/image/upload/site/hero.jpg";

describe("parseSiteImages", () => {
  it("maps the API's keys to { url, alt } entries", () => {
    expect(
      parseSiteImages({
        home_hero: { url: CLOUDINARY, alt: "Ferns by the espresso bar" },
        partner_hero: null,
        why_image: { url: "http://localhost:8000/media/site/why.jpg", alt: "Potting plants" },
      })
    ).toEqual({
      homeHero: { url: CLOUDINARY, alt: "Ferns by the espresso bar" },
      partnerHero: null,
      why: { url: "http://localhost:8000/media/site/why.jpg", alt: "Potting plants" },
    });
  });

  it.each([null, undefined, "oops", 42, []])(
    "returns no images when the response is %s (endpoint missing or down)",
    (data) => {
      expect(parseSiteImages(data)).toEqual(NO_SITE_IMAGES);
    }
  );

  it("treats missing fields as no image (older backend)", () => {
    expect(parseSiteImages({ home_hero: { url: CLOUDINARY, alt: "x" } })).toEqual({
      ...NO_SITE_IMAGES,
      homeHero: { url: CLOUDINARY, alt: "x" },
    });
  });
});

describe("parseSiteImage", () => {
  it.each([
    ["no url", { alt: "x" }],
    ["empty url", { url: "", alt: "x" }],
    ["non-string url", { url: 5, alt: "x" }],
    ["relative url", { url: "/media/site/hero.jpg", alt: "x" }],
    ["non-http url", { url: "javascript:alert(1)", alt: "x" }],
  ])("returns null for %s", (_label, value) => {
    expect(parseSiteImage(value)).toBeNull();
  });

  it("keeps the image with empty alt text if alt is missing", () => {
    expect(parseSiteImage({ url: CLOUDINARY })).toEqual({ url: CLOUDINARY, alt: "" });
  });
});

describe("isOptimizableImage", () => {
  it("is true only for https Cloudinary URLs", () => {
    expect(isOptimizableImage(CLOUDINARY)).toBe(true);
    expect(isOptimizableImage("http://localhost:8000/media/site/hero.jpg")).toBe(false);
    expect(isOptimizableImage("https://example.com/hero.jpg")).toBe(false);
    expect(isOptimizableImage("not a url")).toBe(false);
  });
});
