const FAQS = [
  {
    question: "Who waters and maintains the plants?",
    // TODO(copy)
    answer: "We do — a Forks And Farms team member visits on a regular schedule.",
  },
  {
    question: "What if a plant dies or gets damaged?",
    answer: "We replace it. That's part of what you're paying for.",
  },
  {
    question: "How much space do we need?",
    answer: "As little as a single shelf, up to a full installation — we'll size it to your space on the walkthrough.",
  },
  {
    question: "Is there a contract or commitment?",
    answer: "TODO(copy)",
  },
  {
    question: "How does the revenue share work?",
    answer: "TODO(copy)",
  },
  {
    question: "What does it cost us?",
    answer: "TODO(copy)",
  },
] as const;

// Accordion (spec §3.4.7). Native <details>/<summary> gives keyboard and
// screen-reader support for free — no custom JS, ARIA, or focus
// management needed to make this accessible.
export default function PartnerFAQ() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-7 sm:px-6">
      <h2 className="text-forest">Frequently asked questions</h2>
      <div className="mt-4 divide-y divide-forest/10 rounded-lg border border-forest/10 bg-white">
        {FAQS.map((faq) => (
          <details key={faq.question} className="group p-4 open:pb-4">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-3 font-medium text-forest marker:content-none">
              {faq.question}
              <span
                aria-hidden="true"
                className="shrink-0 text-forest/50 transition-transform group-open:rotate-45"
              >
                +
              </span>
            </summary>
            <p className="mt-2 text-sm text-forest/70">{faq.answer}</p>
          </details>
        ))}
      </div>
    </section>
  );
}
