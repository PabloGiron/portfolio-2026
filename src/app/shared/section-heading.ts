import { Component, computed, input } from '@angular/core';

/** Pixel-font index label (with the section's altitude) plus the section's h2. */
@Component({
  selector: 'app-section-heading',
  template: `
    <p [class]="labelClass()">No. {{ index() }} · {{ label() }} · Alt {{ altitude() }}</p>
    <h2 [id]="headingId()" class="text-4xl font-bold tracking-tight md:text-5xl">{{ title() }}</h2>
  `,
  host: { class: 'flex flex-col gap-6' },
})
export class SectionHeading {
  readonly index = input.required<string>();
  readonly label = input.required<string>();
  readonly title = input.required<string>();
  readonly headingId = input.required<string>();
  /** How high above the ground this section is, e.g. "400 km". */
  readonly altitude = input.required<string>();
  /** Put the label on a dark pill, for sections whose sky gets light. */
  readonly pill = input(false);

  protected readonly labelClass = computed(
    () =>
      'self-start font-pixel text-[13px]' +
      (this.pill() ? ' rounded-md bg-space px-2.5 py-1.5 text-cream' : ''),
  );
}
