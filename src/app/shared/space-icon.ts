import { Component, input } from '@angular/core';
import { SpaceIconName } from '../content';

/** Small low-poly space object. Decorative: always hidden from assistive tech. */
@Component({
  selector: 'app-space-icon',
  template: `
    <svg aria-hidden="true" viewBox="0 0 44 44" [attr.width]="size()" [attr.height]="size()">
      @switch (name()) {
        @case ('planet') {
          <circle cx="22" cy="22" r="12" fill="#3b657a" />
          <polygon points="14,14 22,10 28,18 18,22" fill="#5b8aa3" />
          <g transform="rotate(-20 22 22)">
            <ellipse cx="22" cy="22" rx="20" ry="5" fill="none" stroke="#e9f0c9" stroke-width="2" />
          </g>
        }
        @case ('rocket') {
          <polygon points="22,3 30,18 30,32 14,32 14,18" fill="#e9f0c9" />
          <polygon points="22,3 30,18 22,18" fill="#c8d3bd" />
          <circle cx="22" cy="22" r="4" fill="#3b657a" />
          <polygon points="14,26 6,36 14,34" fill="#9cc3d8" />
          <polygon points="30,26 38,36 30,34" fill="#9cc3d8" />
          <polygon points="18,32 26,32 22,42" fill="#e9c46a" />
        }
        @case ('moon') {
          <circle cx="22" cy="22" r="17" fill="#c8d3bd" />
          <polygon points="22,5 39,22 22,39 28,22" fill="#9fb6c2" />
          <circle cx="15" cy="17" r="4" fill="#9fb6c2" />
          <circle cx="19" cy="29" r="3" fill="#9fb6c2" />
        }
        @case ('star') {
          <polygon points="22,2 27,17 42,22 27,27 22,42 17,27 2,22 17,17" fill="#e9c46a" />
          <polygon points="22,2 27,17 22,22" fill="#b8923a" />
        }
        @case ('sun') {
          <circle cx="22" cy="22" r="15" fill="#e9c46a" />
          <polygon points="22,7 37,22 22,37 27,22" fill="#b8923a" />
          <circle cx="15" cy="18" r="3" fill="#b8923a" />
        }
        @case ('satellite') {
          <rect x="17" y="15" width="10" height="14" fill="#e9f0c9" />
          <rect x="3" y="18" width="12" height="8" fill="#9cc3d8" />
          <rect x="29" y="18" width="12" height="8" fill="#9cc3d8" />
          <rect x="15" y="21" width="2" height="2" fill="#e9f0c9" />
          <rect x="27" y="21" width="2" height="2" fill="#e9f0c9" />
          <line x1="22" y1="15" x2="22" y2="8" stroke="#e9f0c9" stroke-width="1.5" />
          <circle cx="22" cy="7" r="2" fill="#e9c46a" />
        }
      }
    </svg>
  `,
  host: { class: 'inline-flex' },
})
export class SpaceIcon {
  readonly name = input.required<SpaceIconName>();
  readonly size = input(44);
}
