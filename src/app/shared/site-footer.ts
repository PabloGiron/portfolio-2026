import { Component } from '@angular/core';
import { PROFILE } from '../content';

/** The strip under the office floor, at the very bottom of the page. */
@Component({
  selector: 'app-site-footer',
  template: `
    <footer class="bg-soil px-6 pt-5 pb-8 md:px-16">
      <div class="mx-auto flex max-w-[1312px] flex-wrap justify-between gap-x-10 gap-y-3 text-sm">
        <span>© {{ profile.year }} {{ profile.name }}</span>
        <span class="font-pixel text-xs">Game saved. Welcome home.</span>
      </div>
    </footer>
  `,
  host: { class: 'block' },
})
export class SiteFooter {
  protected readonly profile = PROFILE;
}
