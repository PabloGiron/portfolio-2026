import { Component } from '@angular/core';
import { PROFILE } from '../content';

@Component({
  selector: 'app-site-nav',
  template: `
    <header
      class="mx-auto flex w-full max-w-[1440px] flex-wrap items-center justify-between gap-4 px-6 py-5 md:px-16"
    >
      <a href="#top" class="font-display text-xl font-bold no-underline">{{ profile.name }}</a>
      <nav aria-label="Sections">
        <ul class="flex flex-wrap items-center gap-x-8 gap-y-2 text-[15px] font-medium">
          <li><a class="inline-block py-3 no-underline hover:text-sky" href="#about">About</a></li>
          <li>
            <a class="inline-block py-3 no-underline hover:text-sky" href="#experience">Experience</a>
          </li>
          <li>
            <a class="inline-block py-3 no-underline hover:text-sky" href="#projects">Projects</a>
          </li>
          <li>
            <a
              class="inline-flex min-h-11 items-center rounded-lg border border-cream px-5 no-underline hover:border-sky hover:text-sky"
              href="#contact"
              >Let's talk</a
            >
          </li>
        </ul>
      </nav>
    </header>
  `,
})
export class SiteNav {
  protected readonly profile = PROFILE;
}
