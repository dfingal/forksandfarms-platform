// "Why Forks And Farms" mission/story block (spec §3.4.2).
export default function WhyForksAndFarms() {
  return (
    <section className="mx-auto grid max-w-6xl gap-6 px-4 py-7 sm:px-6 lg:grid-cols-2 lg:items-center">
      {/* Photo placeholder — TODO(assets) */}
      <div
        role="img"
        aria-label="Forks And Farms at work (placeholder)"
        className="order-last flex aspect-[4/3] items-center justify-center rounded-lg border border-forest/10 bg-forest/5 text-sm text-forest/50 lg:order-first"
      >
        Photo coming soon
      </div>

      <div>
        <h2 className="text-forest">Why Forks And Farms</h2>
        {/* TODO(copy): 2-3 sentence mission/story */}
        <p className="mt-2 text-forest/80">
          We started Forks And Farms because the places we love in St. Louis deserved more
          life in them. We handpick, deliver, and maintain plants in local coffee shops, wine
          bars, and restaurants — so owners get the look without the upkeep, and customers get
          a reason to stay a little longer.
        </p>
      </div>
    </section>
  );
}
