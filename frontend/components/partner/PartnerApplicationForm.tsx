"use client";

import { useRef, useState, type FormEvent, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { submitPartnerApplication } from "@/lib/api";
import { VENUE_TYPE_LABELS, INTERESTED_TIER_LABELS } from "@/lib/labels";
import { CONTACT_EMAIL } from "@/lib/nav-links";
import type { InterestedTier, VenueType } from "@/lib/types";
import TurnstileWidget, { type TurnstileWidgetHandle } from "./TurnstileWidget";
import { THANKS_NAME_KEY } from "@/lib/partnerStorage";

const VENUE_TYPES = Object.keys(VENUE_TYPE_LABELS) as VenueType[];
const INTERESTED_TIERS = Object.keys(INTERESTED_TIER_LABELS) as InterestedTier[];

interface FormState {
  contact_name: string;
  email: string;
  phone: string;
  venue_name: string;
  venue_type: VenueType | "";
  address: string;
  space_description: string;
  interested_tiers: InterestedTier[];
  referral_source: string;
  notes: string;
}

const INITIAL_STATE: FormState = {
  contact_name: "",
  email: "",
  phone: "",
  venue_name: "",
  venue_type: "",
  address: "",
  space_description: "",
  interested_tiers: [],
  referral_source: "",
  notes: "",
};

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

type FieldErrors = Partial<Record<keyof FormState | "turnstile_token", string>>;

export default function PartnerApplicationForm() {
  const router = useRouter();
  const turnstileRef = useRef<TurnstileWidgetHandle>(null);

  const [form, setForm] = useState<FormState>(INITIAL_STATE);
  const [turnstileToken, setTurnstileToken] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function toggleTier(tier: InterestedTier) {
    setForm((f) => ({
      ...f,
      interested_tiers: f.interested_tiers.includes(tier)
        ? f.interested_tiers.filter((t) => t !== tier)
        : [...f.interested_tiers, tier],
    }));
  }

  function validate(): FieldErrors {
    const errors: FieldErrors = {};
    if (!form.contact_name.trim()) errors.contact_name = "Enter your name.";
    if (!form.email.trim()) errors.email = "Enter your email.";
    else if (!EMAIL_RE.test(form.email.trim())) errors.email = "Enter a valid email.";
    if (!form.venue_name.trim()) errors.venue_name = "Enter your venue's name.";
    if (!form.venue_type) errors.venue_type = "Choose a venue type.";
    if (!form.address.trim()) errors.address = "Enter an address.";
    if (form.interested_tiers.length === 0) {
      errors.interested_tiers = "Select at least one option.";
    }
    if (!turnstileToken) errors.turnstile_token = "Please complete the verification.";
    return errors;
  }

  function focusField(key: string) {
    document.getElementById(key)?.focus();
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitError(null);

    const errors = validate();
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      focusField(Object.keys(errors)[0]);
      return;
    }

    setFieldErrors({});
    setSubmitting(true);

    const result = await submitPartnerApplication({
      contact_name: form.contact_name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim() || undefined,
      venue_name: form.venue_name.trim(),
      venue_type: form.venue_type as VenueType,
      address: form.address.trim(),
      space_description: form.space_description.trim() || undefined,
      interested_tiers: form.interested_tiers,
      referral_source: form.referral_source.trim() || undefined,
      notes: form.notes.trim() || undefined,
      turnstile_token: turnstileToken,
    });

    if (result.ok) {
      try {
        const firstName = form.contact_name.trim().split(/\s+/)[0] || "";
        sessionStorage.setItem(THANKS_NAME_KEY, firstName);
      } catch {
        // Private browsing / storage disabled — /partner/thanks falls back
        // to a generic "Thanks!" when it can't read anything back.
      }
      router.push("/partner/thanks");
      return;
    }

    // Tokens are single-use — any failure (validation, rate limit, server
    // error) needs a fresh one before the visitor can try again.
    turnstileRef.current?.reset();
    setTurnstileToken("");
    setSubmitting(false);

    if (result.status === 429) {
      setSubmitError("Too many attempts — please try again later.");
    } else if (result.status === 0 || result.status >= 500) {
      setSubmitError(
        `Something went wrong submitting your application. Please try again, or email ${CONTACT_EMAIL} directly.`
      );
    } else if (result.errors) {
      const apiErrors: FieldErrors = {};
      for (const [key, messages] of Object.entries(result.errors)) {
        if (key in INITIAL_STATE || key === "turnstile_token") {
          apiErrors[key as keyof FieldErrors] = Array.isArray(messages)
            ? messages.join(" ")
            : String(messages);
        }
      }
      if (Object.keys(apiErrors).length > 0) {
        setFieldErrors(apiErrors);
        focusField(Object.keys(apiErrors)[0]);
      } else {
        setSubmitError(
          `We couldn't process that application. Please check the form, or email ${CONTACT_EMAIL} directly.`
        );
      }
    } else {
      setSubmitError(
        `Something went wrong submitting your application. Please try again, or email ${CONTACT_EMAIL} directly.`
      );
    }
  }

  return (
    <section id="apply" className="scroll-mt-24 mx-auto max-w-2xl px-4 py-7 sm:px-6">
      <h2 className="text-forest">Tell us about your venue</h2>
      <p className="mt-2 text-sm text-forest/70">We&rsquo;ll reply to schedule a walkthrough.</p>

      <form noValidate onSubmit={handleSubmit} className="mt-6 space-y-5">
        {submitError && (
          <p
            role="alert"
            className="rounded border border-terracotta/30 bg-terracotta/5 px-4 py-3 text-sm text-terracotta"
          >
            {submitError}
          </p>
        )}

        <Field label="Contact name" id="contact_name" error={fieldErrors.contact_name} required>
          <input
            id="contact_name"
            type="text"
            value={form.contact_name}
            onChange={(e) => update("contact_name", e.target.value)}
            aria-invalid={!!fieldErrors.contact_name}
            aria-describedby={fieldErrors.contact_name ? "contact_name-error" : undefined}
            className={inputClass(!!fieldErrors.contact_name)}
          />
        </Field>

        <Field label="Email" id="email" error={fieldErrors.email} required>
          <input
            id="email"
            type="email"
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
            aria-invalid={!!fieldErrors.email}
            aria-describedby={fieldErrors.email ? "email-error" : undefined}
            className={inputClass(!!fieldErrors.email)}
          />
        </Field>

        <Field label="Phone" id="phone" error={fieldErrors.phone}>
          <input
            id="phone"
            type="tel"
            value={form.phone}
            onChange={(e) => update("phone", e.target.value)}
            className={inputClass(false)}
          />
        </Field>

        <Field label="Venue name" id="venue_name" error={fieldErrors.venue_name} required>
          <input
            id="venue_name"
            type="text"
            value={form.venue_name}
            onChange={(e) => update("venue_name", e.target.value)}
            aria-invalid={!!fieldErrors.venue_name}
            aria-describedby={fieldErrors.venue_name ? "venue_name-error" : undefined}
            className={inputClass(!!fieldErrors.venue_name)}
          />
        </Field>

        <Field label="Venue type" id="venue_type" error={fieldErrors.venue_type} required>
          <select
            id="venue_type"
            value={form.venue_type}
            onChange={(e) => update("venue_type", e.target.value as VenueType)}
            aria-invalid={!!fieldErrors.venue_type}
            aria-describedby={fieldErrors.venue_type ? "venue_type-error" : undefined}
            className={inputClass(!!fieldErrors.venue_type)}
          >
            <option value="">Choose one…</option>
            {VENUE_TYPES.map((type) => (
              <option key={type} value={type}>
                {VENUE_TYPE_LABELS[type]}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Address" id="address" error={fieldErrors.address} required>
          <input
            id="address"
            type="text"
            value={form.address}
            onChange={(e) => update("address", e.target.value)}
            aria-invalid={!!fieldErrors.address}
            aria-describedby={fieldErrors.address ? "address-error" : undefined}
            className={inputClass(!!fieldErrors.address)}
          />
        </Field>

        <Field
          label="Approx. space or number of plants"
          id="space_description"
          error={fieldErrors.space_description}
        >
          <input
            id="space_description"
            type="text"
            value={form.space_description}
            onChange={(e) => update("space_description", e.target.value)}
            className={inputClass(false)}
          />
        </Field>

        <fieldset>
          <legend className="mb-1 block text-sm font-medium text-forest">
            Interested in <span aria-hidden="true">*</span>
            <span className="sr-only">(required)</span>
          </legend>
          <div
            id="interested_tiers"
            className="space-y-2"
            aria-invalid={!!fieldErrors.interested_tiers}
            aria-describedby={fieldErrors.interested_tiers ? "interested_tiers-error" : undefined}
          >
            {INTERESTED_TIERS.map((tier) => (
              <label key={tier} className="flex items-center gap-2 text-sm text-forest">
                <input
                  type="checkbox"
                  checked={form.interested_tiers.includes(tier)}
                  onChange={() => toggleTier(tier)}
                  className="h-4 w-4 rounded border-forest/30 text-forest focus-visible:outline-terracotta"
                />
                {INTERESTED_TIER_LABELS[tier]}
              </label>
            ))}
          </div>
          {fieldErrors.interested_tiers && (
            <p id="interested_tiers-error" className="mt-1 text-sm text-terracotta">
              {fieldErrors.interested_tiers}
            </p>
          )}
        </fieldset>

        <Field
          label="How did you hear about us?"
          id="referral_source"
          error={fieldErrors.referral_source}
        >
          <input
            id="referral_source"
            type="text"
            value={form.referral_source}
            onChange={(e) => update("referral_source", e.target.value)}
            className={inputClass(false)}
          />
        </Field>

        <Field label="Notes" id="notes" error={fieldErrors.notes}>
          <textarea
            id="notes"
            rows={4}
            value={form.notes}
            onChange={(e) => update("notes", e.target.value)}
            className={inputClass(false)}
          />
        </Field>

        <div>
          <TurnstileWidget ref={turnstileRef} onVerify={setTurnstileToken} />
          {fieldErrors.turnstile_token && (
            <p id="turnstile_token-error" className="mt-1 text-sm text-terracotta">
              {fieldErrors.turnstile_token}
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded bg-forest px-5 py-2.5 text-sm font-semibold text-cream hover:bg-forest/90 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
        >
          {submitting ? "Sending…" : "Submit application"}
        </button>
      </form>

      <p className="mt-4 text-sm text-forest/70">
        Prefer to talk? Email{" "}
        <a href={`mailto:${CONTACT_EMAIL}`} className="font-medium text-terracotta hover:underline">
          {CONTACT_EMAIL}
        </a>
        {/* TODO: confirm this is the right address */}
      </p>
    </section>
  );
}

function inputClass(invalid: boolean) {
  return `w-full rounded border bg-white px-3 py-2 text-sm text-forest ${
    invalid ? "border-terracotta" : "border-forest/20"
  }`;
}

interface FieldProps {
  label: string;
  id: string;
  error?: string;
  required?: boolean;
  children: ReactNode;
}

function Field({ label, id, error, required, children }: FieldProps) {
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-forest">
        {label}
        {required && (
          <>
            <span aria-hidden="true"> *</span>
            <span className="sr-only"> (required)</span>
          </>
        )}
      </label>
      {children}
      {error && (
        <p id={`${id}-error`} className="mt-1 text-sm text-terracotta">
          {error}
        </p>
      )}
    </div>
  );
}
