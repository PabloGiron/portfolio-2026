import { Component } from '@angular/core';

/** A low-poly cloud lit by the sunset. Decorative; size and position come from the host's classes. */
@Component({
  selector: 'app-cloud',
  template: `
    <svg aria-hidden="true" viewBox="0 0 200 80" class="block h-auto w-full">
      <polygon points="6,72 26,44 58,38 78,14 122,10 144,32 172,38 194,72" fill="#fbe6d4" />
      <polygon points="78,14 122,10 144,32 104,46" fill="#fff4e8" />
      <polygon points="6,72 194,72 172,60 30,60" fill="#e3b3a6" />
    </svg>
  `,
  host: { class: 'pointer-events-none block' },
})
export class Cloud {}
