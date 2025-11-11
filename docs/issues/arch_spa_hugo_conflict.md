[15 tools called]

## Diagnosis

- **Dual-mode template swapping breaks stability**  
  SPA toggle overwrites Hugo’s core layouts with SPA copies (`baseof.html`, `list.html`, `single.html`) every time the helper script runs, so the project constantly flips between two incompatible template stacks. That destroys the PaperMod inheritance chain and prevents you from keeping “traditional” and SPA layouts in sync.<br>

  ```32:35:scripts/toggle-spa-mode.sh
    cp layouts/_default/baseof-spa.html layouts/_default/baseof.html
    cp layouts/_default/list-spa.html layouts/_default/list.html
    cp layouts/_default/single-spa.html layouts/_default/single.html
  ```

- **SPA navigation is hard-coded and misses real menu entries**  
  The SPA shell only knows about the sections listed in its JS map, so any new or localized menu item (e.g. `/zh/about`, `/zh/search`) is ignored. Clicking those links sets `preventDefault`, then the router can’t resolve them, which looks like a “broken” left nav even though the underlying Hugo routes work.<br>

  ```379:410:layouts/_default/baseof-spa.html
                const urls = {
                    'home': '/',
                    'my_insights': '/categories/my_insights',
                    ...
                    'courses': '/categories/courses',
                    'search': '/search'
                };
  ```

- **SPA fetches strip scripts, so search/UI logic silently dies**  
  When the SPA loads a page it pulls only the inner HTML of `<main>` and injects it via `innerHTML`. That drops every `<script>` tag on the destination page, so components like the enhanced search page never re-initialize unless you hard-refresh. This matches the “search works sometimes” symptom.<br>

  ```346:411:layouts/_default/baseof-spa.html
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const mainContent = doc.querySelector('main') || doc.querySelector('#content-container');
                
                return mainContent ? mainContent.innerHTML : '<div>Content not found</div>';
  ```

- **Tailwind CDN + huge bespoke CSS fights PaperMod styling**  
  The SPA base injects Tailwind’s CDN build on top of PaperMod’s pipeline, so Tailwind Preflight keeps re-normalizing the DOM and overriding theme colors/spacing. Combined with a 2,000+ line `custom.css` full of non-standard selectors like `:contains()` (unsupported in CSS), you end up with order-dependent overrides—hence the “colors suddenly change” and layout jitter.<br>

  ```7:21:layouts/_default/baseof-spa.html
    {{- $styles := slice (resources.Get "css/main.css") -}}
    ...
    <script src="https://cdn.tailwindcss.com"></script>
  ```

  ```1199:1225:assets/css/custom.css

.post-content h2:contains("参考"),
...
.post-content h2:contains("参考文献")::after,

  ```

- **Duplicate search implementations compete**  
  The header partial and SPA list templates each hot-load Fuse.js from the CDN and register their own listeners. Depending on which version initializes first (or survives the SPA swap), search can behave differently across pages, adding to the “works, then doesn’t” experience.<br>
  ```1:128:layouts/partials/header.html
<header class="navbar-glass">
...
                const input = document.getElementById('headerSearch');
...
                const fuse = new Fuse(data, {
  ```

## Suggested Next Steps

- Pick one architecture—PaperMod’s multipage flow or a purpose-built SPA—and remove the toggle/overwrites. If you stay with PaperMod, restore original `baseof/list/single` and move SPA experiments into a separate layout or mount.
- Replace the hard-coded SPA nav map with real menu data (or drop the SPA router entirely) so new sections don’t break navigation.
- If you keep SPA behavior, use progressive enhancement: fetch partials that include scripts, or run component initializers after injection. Otherwise, revert to full-page navigation where Hugo serves the JS assets.
- Remove Tailwind CDN from the production bundle unless you fully migrate to Tailwind; slim down `custom.css` to focused overrides that work with PaperMod’s variables/utilities.
- Consolidate search into one implementation (likely Hugo’s JSON + a single Fuse.js client) to avoid conflicting listeners.

Once you settle on a single layout strategy and streamline assets, the random regressions should disappear, and future changes will stop undoing previous fixes.
