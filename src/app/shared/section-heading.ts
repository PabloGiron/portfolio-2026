import { Component, input } from '@angular/core';

/** Pixel-font index label plus the section's h2. */
@Component({
  selector: 'app-section-heading',
  template: `
    <p class="font-pixel text-[13px]">No. {{ index() }} · {{ label() }}</p>
    <h2 [id]="headingId()" class="text-4xl font-bold tracking-tight md:text-5xl">{{ title() }}</h2>
  `,
  host: { class: 'flex flex-col gap-6' },
})
export class SectionHeading {
  readonly index = input.required<string>();
  readonly label = input.required<string>();
  readonly title = input.required<string>();
  readonly headingId = input.required<string>();
}
