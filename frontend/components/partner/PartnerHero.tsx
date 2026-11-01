// Partner page hero (spec §3.4.1). "Start the conversation" scrolls to
// the application form (id="apply" on the form section, scroll-mt-24 to
// clear the sticky header — same pattern as the home page's #map).
export default function PartnerHero() {
  return (
    <section className="mx-auto grid max-w-6xl gap-6 px-4 py-7 sm:px-6 sm:py-11 lg:grid-cols-2 lg:items-center">
      <div>
        <h1 className="text-forest">Plants that pay their way.</h1>
        {/* TODO(copy): real one-line pitch */}
        <p className="mt-3 max-w-md text-forest/80">
          Turn your space into somewhere people want to linger — we supply, style, and care
          for the plants, you keep a share of what sells.
        </p>

        <div className="mt-4">
          <a
            href="#apply"
            className="inline-block rounded bg-forest px-5 py-2.5 text-sm font-semibold text-cream hover:bg-forest/90"
          >
            Start the conversation
          </a>
        </div>
      </div>

      {/* Photo placeholder — TODO(assets): real photo of plants in a venue */}
      <div
        role="img"
        aria-label="Plants on display at a Forks And Farms partner venue (placeholder)"
        className="flex aspect-[4/3] items-center justify-center rounded-lg border border-forest/10 bg-forest/5 text-sm text-forest/50"
      >
        Photo coming soon
      </div>
    </section>
  );
}
