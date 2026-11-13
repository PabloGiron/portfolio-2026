import { Component } from '@angular/core';
import { About } from './sections/about';
import { Contact } from './sections/contact';
import { Experience } from './sections/experience';
import { Hero } from './sections/hero';
import { Projects } from './sections/projects';
import { SiteFooter } from './shared/site-footer';
import { SiteNav } from './shared/site-nav';

@Component({
  selector: 'app-root',
  imports: [SiteNav, Hero, About, Experience, Projects, Contact, SiteFooter],
  template: `
    <a
      href="#main"
      class="sr-only focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:z-50 focus:rounded-lg focus:bg-cream focus:px-4 focus:py-3 focus:font-semibold focus:text-space"
      >Skip to content</a
    >
    <app-site-nav />
    <main id="main">
      <app-hero />
      <app-about />
      <app-experience />
      <app-projects />
      <app-contact />
    </main>
    <app-site-footer />
  `,
})
export class App {}
