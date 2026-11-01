// sessionStorage key shared between PartnerApplicationForm (writes the
// first name on success) and ThanksContent (reads it). Never holds the
// email — the thanks page doesn't echo it back (see spec §3.5).
export const THANKS_NAME_KEY = "ff_partner_first_name";
