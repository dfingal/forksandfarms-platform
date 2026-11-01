const STEPS = [
  { number: "01", title: "Apply", body: "Tell us about your space below." },
  { number: "02", title: "Walkthrough", body: "We visit and plan the right setup together." },
  { number: "03", title: "Install", body: "We bring and place the plants." },
  { number: "04", title: "Ongoing care", body: "We handle watering, rotation, and replacements." },
] as const;

// "How it works" (spec §3.4.6).
export default function HowItWorks() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-7 sm:px-6">
      <h2 className="text-forest">How it works</h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-4">
        {STEPS.map((step) => (
          <div key={step.number}>
            <p className="text-sm font-semibold text-terracotta">{step.number}</p>
            <h3 className="mt-1 text-forest">{step.title}</h3>
            <p className="mt-1 text-sm text-forest/70">{step.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
