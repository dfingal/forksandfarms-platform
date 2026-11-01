"use client";

import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import Script from "next/script";

declare global {
  interface Window {
    turnstile?: {
      render: (
        container: HTMLElement,
        options: {
          sitekey: string;
          callback: (token: string) => void;
          "expired-callback"?: () => void;
          "error-callback"?: () => void;
        }
      ) => string;
      reset: (widgetId: string) => void;
      remove: (widgetId: string) => void;
    };
    // Named in the script's ?onload= query param below — Cloudflare calls
    // this once the Turnstile API itself (not just the script tag) is
    // ready, which is the reliable signal to render (next/script's own
    // onLoad can fire before window.turnstile actually exists).
    onloadTurnstileCallback?: () => void;
  }
}

const SITE_KEY = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;

export interface TurnstileWidgetHandle {
  /** Tokens are single-use — call this after any failed submission so
   * the next attempt gets a fresh token instead of silently failing. */
  reset: () => void;
}

interface TurnstileWidgetProps {
  onVerify: (token: string) => void;
}

const TurnstileWidget = forwardRef<TurnstileWidgetHandle, TurnstileWidgetProps>(
  function TurnstileWidget({ onVerify }, ref) {
    const containerRef = useRef<HTMLDivElement>(null);
    const widgetIdRef = useRef<string | null>(null);

    useImperativeHandle(ref, () => ({
      reset: () => {
        if (widgetIdRef.current && window.turnstile) {
          window.turnstile.reset(widgetIdRef.current);
        }
      },
    }));

    useEffect(() => {
      if (!SITE_KEY || !containerRef.current) return;

      let cancelled = false;
      const container = containerRef.current;

      function render() {
        if (cancelled || !window.turnstile || !container) return;
        widgetIdRef.current = window.turnstile.render(container, {
          sitekey: SITE_KEY!,
          callback: (token) => onVerify(token),
          "expired-callback": () => onVerify(""),
          "error-callback": () => onVerify(""),
        });
      }

      if (window.turnstile) {
        render();
      } else {
        window.onloadTurnstileCallback = render;
      }

      return () => {
        cancelled = true;
        if (widgetIdRef.current && window.turnstile) {
          window.turnstile.remove(widgetIdRef.current);
        }
      };
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    if (!SITE_KEY) {
      return (
        <p className="text-sm text-terracotta">
          Spam check unavailable (missing site key) — applications can&rsquo;t be submitted
          right now.
        </p>
      );
    }

    return (
      <>
        <Script
          src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback&render=explicit"
          strategy="afterInteractive"
        />
        <div ref={containerRef} />
      </>
    );
  }
);

export default TurnstileWidget;
