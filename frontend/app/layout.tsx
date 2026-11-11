import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { DEFAULT_SHARE_IMAGE, getSiteUrl, SITE_NAME } from "@/lib/seo";
import { BRAND_COLORS } from "@/lib/brand";

// Placeholder typeface choices (CLAUDE.md: mark with TODO where final
// decisions aren't made yet) — swap for the brand's chosen fonts later.
const bodyFont = Geist({
  variable: "--font-body",
  subsets: ["latin"],
});

const monoFont = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const siteUrl = getSiteUrl();

export const metadata: Metadata = {
  // Makes relative metadata URLs (share image, canonical paths) absolute.
  // Left unset if NEXT_PUBLIC_SITE_URL isn't configured.
  ...(siteUrl ? { metadataBase: siteUrl } : {}),
  title: SITE_NAME,
  description: "Plants in the places you already go.", // TODO(copy)
  // Site-wide share image, for pages that don't set their own (city and
  // venue pages do, via lib/seo.ts).
  openGraph: { siteName: SITE_NAME, type: "website", images: [DEFAULT_SHARE_IMAGE] },
  twitter: { card: "summary_large_image", images: [DEFAULT_SHARE_IMAGE.url] },
};

// Tints the browser UI (e.g. the mobile address bar) in brand green.
export const viewport: Viewport = {
  themeColor: BRAND_COLORS.forest,
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${bodyFont.variable} ${monoFont.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-cream text-foreground">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
