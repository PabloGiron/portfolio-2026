import { Component, input } from '@angular/core';
import { SpaceIconName } from '../content';

/** Small low-poly icon: space objects, hobbies, a web page, a phone and a cart. Decorative: always hidden from assistive tech. */
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
        @case ('gamepad') {
          <polygon points="5,14 39,14 42,34 34,34 29,27 15,27 10,34 2,34" fill="#e9f0c9" />
          <polygon points="15,27 29,27 34,34 42,34 41,29 3,29 2,34 10,34" fill="#c8d3bd" />
          <rect x="9" y="19" width="8" height="2.5" fill="#3b657a" />
          <rect x="11.75" y="16.25" width="2.5" height="8" fill="#3b657a" />
          <circle cx="30" cy="18" r="2.2" fill="#e9c46a" />
          <circle cx="35" cy="22" r="2.2" fill="#3b657a" />
        }
        @case ('shoe') {
          <polygon points="4,12 13,12 20,21 34,25 41,30 41,34 4,34" fill="#e9f0c9" />
          <polygon points="4,12 10,12 10,34 4,34" fill="#c8d3bd" />
          <polygon points="17,23 22,22 20,34 15,34" fill="#e9c46a" />
          <polygon points="24,24 29,24 27,34 22,34" fill="#e9c46a" />
          <rect x="3" y="34" width="39" height="4" fill="#9cc3d8" />
        }
        @case ('book') {
          <polygon points="3,10 22,14 22,38 3,34" fill="#e9f0c9" />
          <polygon points="41,10 22,14 22,38 41,34" fill="#c8d3bd" />
          <g stroke="#3b657a" stroke-width="1.5">
            <line x1="7" y1="17" x2="18" y2="19.3" />
            <line x1="7" y1="23" x2="18" y2="25.3" />
            <line x1="7" y1="29" x2="18" y2="31.3" />
          </g>
          <polygon points="30,12.3 35,11.3 35,24 32.5,21.5 30,25" fill="#e9c46a" />
        }
        @case ('dumbbell') {
          <g transform="rotate(-20 22 22)">
            <rect x="12" y="20" width="20" height="4" fill="#c8d3bd" />
            <rect x="7" y="11" width="6" height="22" fill="#e9f0c9" />
            <rect x="31" y="11" width="6" height="22" fill="#e9f0c9" />
            <rect x="2" y="15" width="5" height="14" fill="#9cc3d8" />
            <rect x="37" y="15" width="5" height="14" fill="#9cc3d8" />
          </g>
        }
        @case ('webpage') {
          <rect x="3" y="7" width="38" height="30" fill="#e9f0c9" />
          <rect x="3" y="7" width="38" height="6" fill="#9cc3d8" />
          <circle cx="7" cy="10" r="1.2" fill="#3b657a" />
          <circle cx="11" cy="10" r="1.2" fill="#3b657a" />
          <circle cx="13" cy="21" r="4.5" fill="#e9c46a" />
          <rect x="21" y="17.5" width="15" height="2.5" fill="#3b657a" />
          <rect x="21" y="22" width="10" height="2.5" fill="#9fb6c2" />
          <rect x="7" y="29" width="8" height="5" fill="#c8d3bd" />
          <rect x="18" y="29" width="8" height="5" fill="#c8d3bd" />
          <rect x="29" y="29" width="8" height="5" fill="#c8d3bd" />
        }
        @case ('phone') {
          <rect x="11" y="3" width="22" height="38" rx="3" fill="#e9f0c9" />
          <rect x="13.5" y="8" width="17" height="26" fill="#3b657a" />
          <circle cx="22" cy="16" r="4" fill="#e9c46a" />
          <rect x="16" y="23" width="12" height="2.5" fill="#e9f0c9" />
          <rect x="16" y="27.5" width="8" height="2.5" fill="#9cc3d8" />
          <rect x="19" y="36.5" width="6" height="1.8" fill="#9fb6c2" />
        }
        @case ('cart') {
          <polyline points="2,8 9,8 14,28 36,28" fill="none" stroke="#e9f0c9" stroke-width="2.5" />
          <polygon points="10.5,12 41,12 36,24 13.5,24" fill="#e9c46a" />
          <polygon points="10.5,12 26,12 24,24 13.5,24" fill="#b8923a" />
          <circle cx="17" cy="35" r="3.5" fill="#e9f0c9" />
          <circle cx="32" cy="35" r="3.5" fill="#e9f0c9" />
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
