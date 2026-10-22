/* e-commerce-audit: count what a shopper can SEE on the current screen.
 *
 * Run this file's text in the rendered page once the screen has settled:
 *   - browser tools: pass the whole file as the script text;
 *   - Playwright:    page.evaluate(open("visible_counts.js").read())
 * It scrolls to the top of the page, then returns a JSON string. If "scrolled_from" in the result is not 0, the
 * page was scrolled and its scroll-driven parts (a header that hides, a buy bar that appears) are stale: run the
 * script a second time and keep the second result. Parse it and store the object under
 * "counts" in the walk log's "screens" list (path_metrics.py also accepts the unparsed string).
 *
 * It counts only what is rendered: not display:none, not zero-size, not transparent, not clipped away
 * by a collapsed parent, not inside a closed <details>, not off-canvas. So a full site menu that the checkout hides does not count.
 * It reads no field values and returns no URLs.
 *
 * Limits (say so in the finding when one applies):
 *   - fields inside a payment provider's iframe are not counted;
 *   - elements inside a web component's shadow root are not counted;
 *   - on a site that wraps the whole page in one <form>, every region reads as "main";
 *   - "covered" tests the centre of a button in the first screen only;
 *   - an absolutely positioned box inside a clipping parent can count although it is cut off;
 *   - an absolutely positioned box below the fold of a fixed window that scrolls (a tall modal) is not counted;
 *   - a card parked to the right of the screen in a swipe carousel is not counted;
 *   - a link whose only child is floated or display:contents has no size and is not counted;
 *   - on a page that scrolls inside a box and not in the window, scroll that box to the top before running;
 *   - primary_candidates is a word match on button text: confirm a count of 0 on the screenshot.
 *
 * The WORDS block is a copy of path_words.json. A test fails when the two differ: edit both.
 */
(() => {
  /*WORDS*/
  const WORDS = {
    "funnel": "kosaric|košaric|narud[zž]b|blagajn|cart|checkout|order|basket|warenkorb|kasse|bestell|carrello|cassa|ordine|nakup|panier|commande|carrito|pedido",
    "primary": "add to (cart|basket|bag)|(dodaj\\S*|stavi\\S*) u ko[sš]ar|^u ko[sš]ar|in den (warenkorb|einkaufswagen)|zum warenkorb hinzuf|aggiungi al carrello|(^|dodaj\\S* )v ko[sš]aric|check ?out|place order|order now|(complete|confirm|submit) (the |my )?(order|purchase)|proceed|continue|^next$|^buy\\b|buy now|\\bpay\\b|naru[cč]i(te)?\\b|(potvrdi|po[sš]alji|dovr[sš]i|zavr[sš]i|zaklju[cč]i)\\S*\\s+narud[zž]b|^potvrdi$|^dalje$|obvez\\S*\\s+pla[cć]anj|^pla[cć]anje$|sljede[cć]i korak|(^|\\s)na pla[cć]anj|^plati|\\splati\\b|nastavi|blagajn|dovr[sš]i|zav.?[sš]i|kupi(te)?\\b|zur kasse|kasse\\b|bestellen|bestellung (abschicken|absenden|abschlie|aufgeben)|kauf abschlie|kostenpflichtig|zahlungspflichtig|bezahlen|kaufen\\b|weiter(?![a-zäöü])|procedi|cassa\\b|al pagamento|effettua l.ordine|(conferma|completa)\\S*\\s+(l.)?(ordine|acquisto)|ordine con obbligo|ordina(?!\\s+per)\\b|\\bpaga(re)?\\b|acquista|continua|^avanti$|nadaljuj|zaklju[cč]i|oddaj|^potrdi$|potrdi\\S*\\s+naro[cč]il|^pla[cč]aj|^naprej$|naro[cč]i\\b|naro[cč]ilo z obvez|na blagajno",
    "not_primary": "continue (shopping|browsing|reading)|keep shopping|check ?out (our|the|this|these|more)|\\(0\\)\\s*$|\\binfo\\b|zatvoren|geschlossen|closed|(buy|order) again|nastavi\\S*\\s+(sa?\\s+)?kup|nastavi\\S*\\s+[cč]ita|kupi\\s+\\d|plati\\s+\\d|buy\\s+\\d|ponovi\\S*\\s+narud|weiter\\s*(ein)?kaufen|weiter\\s*(shoppen|st[oö]bern|lesen)|continua\\S*\\s+(a fare\\s+|con\\s+)?(gli\\s+|lo\\s+)?(acquist|shopping)|continua\\S*\\s+a leggere|nadaljuj\\S*\\s+(z\\s+)?nakup|continuer\\s+(mes\\s+)?achats|\\b(with|s|sa|mit|con|z)\\s+(google|facebook|apple|microsoft)(?!\\S*\\s*pay)|^(back|natrag|zur[uü]ck|indietro|nazaj)\\b|my orders|order history|moje narud|povijest narud|payment methods|na[cč]ini pla[cć]anj",
    "login": "sign in|log ?in|prijav|anmelden|accedi",
    "guest": "bez prijave|ohne anmeld|without (signing|logging) in|as (a )?guest|kao gost|als gast|come ospite|kot gost",
    "search": "search|suche|pretra|tra[zž]i|cerca|iskanj"
  };
  /*END WORDS*/
  const RX = Object.fromEntries(Object.entries(WORDS).map(([k, v]) => [k, new RegExp(v, 'i')]));
  const isPrimary = t => RX.primary.test(t) && !RX.not_primary.test(t) && !(RX.login.test(t) && !RX.guest.test(t));

  const scrolledFrom = Math.round(scrollY);              // not 0: the page has not yet reacted to the jump below
  scrollTo({top: 0, left: 0, behavior: 'instant'});     // 'instant': a page with smooth scrolling would still be mid-scroll
  const vh = innerHeight, vw = innerWidth;
  const shown = e => {
    if (e.checkVisibility && !e.checkVisibility()) return false;      // closed <details>, content-visibility:hidden
    const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    if (r.width <= 1 || r.height <= 1 || s.visibility === 'hidden' || s.display === 'none' || +s.opacity === 0) return false;
    if (r.right <= 0 || r.left >= vw) return false;                     // off-canvas drawers and menus
    // What cuts an element off: a parent that hides its overflow (hidden, clip) on that axis, like a collapsed menu.
    // What does not: a parent that scrolls (auto, scroll) and has more content than room, because the shopper can
    // scroll there. From such a scroller upward, the scroller's own box is what has to be visible, not the element.
    // Fixed and absolute boxes (drawers, banners) escape the parents above them.
    let escY = s.position === 'fixed' || s.position === 'absolute', escX = escY;
    let fixed = s.position === 'fixed';
    let top = r.top, bottom = r.bottom, left = r.left, right = r.right;      // the box that must be visible
    const clips = v => v === 'hidden' || v === 'clip', scrolls = v => v === 'auto' || v === 'scroll';
    for (let n = e.parentElement; n; n = n.parentElement) {
      const p = getComputedStyle(n);
      if (p.display === 'none' || p.visibility === 'hidden' || +p.opacity === 0) return false;
      if (p.display === 'contents') continue;                          // no box of its own: it cannot clip
      const q = n.getBoundingClientRect();
      if (!escY && clips(p.overflowY) && (bottom <= q.top || top >= q.bottom)) return false;
      if (!escX && clips(p.overflowX) && (right <= q.left || left >= q.right)) return false;
      if (!escY && scrolls(p.overflowY) && n.scrollHeight > n.clientHeight + 1) {
        if (q.height <= 1) return false;                                 // a "scroller" collapsed to nothing
        top = q.top; bottom = q.bottom;
      }
      if (!escX && scrolls(p.overflowX) && n.scrollWidth > n.clientWidth + 1) {
        if (q.width <= 1) return false;
        left = q.left; right = q.right;
      }
      if (p.position === 'fixed' || p.position === 'absolute') escY = escX = true;
      if (p.position === 'fixed') fixed = true;
    }
    if (bottom <= 0) return false;                     // parked above the top of the page: a skip link, a hidden panel
    if (fixed && top >= vh) return false;              // a fixed panel parked below the screen
    return true;
  };
  const inFirstScreen = e => { const r = e.getBoundingClientRect(); return r.top >= 0 && r.bottom <= vh; };
  const covered = e => {              // true: something else is drawn over its centre; null: not in the first screen
    const r = e.getBoundingClientRect();
    const x = r.left + r.width / 2, y = r.top + r.height / 2;
    if (x < 0 || x >= vw || y < 0 || y >= vh) return null;
    const top = document.elementFromPoint(x, y);
    if (!top) return null;
    return !(top === e || e.contains(top) || top.contains(e));
  };
  // Page regions only: a <footer> or <header> inside a form, an article or a dialog is not the site's.
  const INNER = 'form, article, [role=dialog]';        // not <main>: some themes wrap the whole page in it
  const pageRegion = (e, tag) => { const r = e.closest(tag); return r && !r.closest(INNER) ? r : null; };
  const region = e => pageRegion(e, 'footer') ? 'footer' : e.closest('nav') ? 'nav' : pageRegion(e, 'header') ? 'header' : 'main';
  const text = e => (e.textContent || e.value || e.getAttribute('aria-label') || e.getAttribute('title') || '')
    .replace(/\s+/g, ' ').trim().slice(0, 40);
  const zero = () => ({header: 0, nav: 0, footer: 0, main: 0});

  const links = zero(), exits = zero();
  for (const a of document.querySelectorAll('a[href]')) {
    if (!shown(a)) continue;
    const h = (a.getAttribute('href') || '').trim().toLowerCase(), g = region(a);
    links[g]++;
    if (h && h !== '#' && !/^(#|javascript:|mailto:|tel:)/.test(h) && !RX.funnel.test(h)) exits[g]++;
  }
  const buttons = [];
  const BUTTONS = 'button, input[type=submit], input[type=button], [role=button], a[class*="btn" i], a[class*="button" i], a[class*="cta" i]';
  for (const b of document.querySelectorAll(BUTTONS)) {
    if (b.querySelector(BUTTONS) || !shown(b)) continue;               // a wrapper around a button: count the inner one
    const t = text(b);
    if (!t) continue;
    buttons.push({text: t, region: region(b), primary_candidate: isPrimary(t), first_screen: inFirstScreen(b),
                  covered: covered(b), top_px: Math.round(b.getBoundingClientRect().top + scrollY)});
  }
  const fields = {typed: 0, typed_required: 0, typed_optional: 0, checkboxes: 0, checkboxes_required: 0,
                  radio_groups: 0, selects: 0, selects_without_default: 0};
  const preTicked = [], preSelectedRadios = [], radios = new Set();
  const isSearch = e => e.type === 'search' || /^(s|q)$/i.test(e.name || '') || !!e.closest('[role=search]')
    || RX.search.test([e.name, e.id, e.form && e.form.id, e.form && e.form.className,
                       e.form && e.form.getAttribute('action')].join(' '));   // not the placeholder: "Search for your address"
  for (const e of document.querySelectorAll('input, select, textarea')) {
    const type = e.tagName === 'INPUT' ? (e.type || 'text').toLowerCase() : e.tagName.toLowerCase();
    if (['hidden', 'submit', 'button', 'image', 'reset'].includes(type)) continue;
    // Styled checkboxes and radios hide the real input (opacity 0) and draw a label: judge those by the label.
    const box = type === 'checkbox' || type === 'radio';
    if (!(box ? shown(e) || shown(e.closest('label') || e.parentElement) : shown(e))) continue;
    if (pageRegion(e, 'footer') || isSearch(e)) continue;               // site search; newsletter in the site footer
    if (type === 'radio') { radios.add(e.name); if (e.defaultChecked) preSelectedRadios.push(e.name || e.id || '(unnamed)'); continue; }
    if (type === 'checkbox') { fields.checkboxes++; if (e.required) fields.checkboxes_required++; if (e.checked) preTicked.push(e.name || e.id || '(unnamed)'); continue; }
    if (type === 'select') { fields.selects++; if (e.selectedIndex <= 0 && !(e.options[0] && e.options[0].value)) fields.selects_without_default++; continue; }
    fields.typed++; if (e.required) fields.typed_required++; else fields.typed_optional++;
  }
  fields.radio_groups = radios.size;
  const sum = o => o.header + o.nav + o.footer + o.main;
  // A cart drawer often sits inside the site header, so only the site footer and menus are excluded.
  const act = buttons.filter(b => b.region !== 'footer' && b.region !== 'nav');
  const prim = act.filter(b => b.primary_candidate);
  return JSON.stringify({
    viewport: [vw, vh], doc_height: document.documentElement.scrollHeight, scrolled_from: scrolledFrom,
    links, links_total: sum(links), exit_links: exits, exit_links_total: sum(exits),
    buttons: act.slice(0, 40), buttons_total: buttons.length,
    primary_buttons: prim.map(b => ({text: b.text, first_screen: b.first_screen, covered: b.covered, top_px: b.top_px})),
    primary_candidates: prim.length, primary_in_first_screen: prim.filter(b => b.first_screen).length,
    primary_covered: prim.filter(b => b.covered === true).length,
    fields, pre_ticked: preTicked, pre_selected_radios: preSelectedRadios,
  });
})()
