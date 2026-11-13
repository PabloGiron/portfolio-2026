import { Component } from '@angular/core';
import { PROFILE } from '../content';

/** The page ends by "landing": a brown planet horizon rises behind the footer. */
@Component({
  selector: 'app-site-footer',
  template: `
    <footer
      class="bg-[radial-gradient(ellipse_75%_100%_at_50%_100%,var(--color-soil)_0,var(--color-soil)_96%,var(--color-soil-light)_97%,var(--color-soil-light)_99%,transparent_100%)] bg-no-repeat px-6 pt-28 pb-8 md:px-16"
    >
      <div
        class="mx-auto flex max-w-[1312px] flex-wrap justify-center gap-x-10 gap-y-3 text-sm text-muted"
      >
        <span>© {{ profile.year }} {{ profile.name }}</span>
        <span class="font-pixel text-xs">Game saved. Safe travels.</span>
      </div>
    </footer>
  `,
  host: { class: 'block' },
})
export class SiteFooter {
  protected readonly profile = PROFILE;
}
