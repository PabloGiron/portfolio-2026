import { Component } from '@angular/core';

/**
 * The fox from the old portfolio's logo, redrawn as a constellation: stars at the corners of
 * its head, joined by faint lines. Decorative; size and position come from the host's classes.
 */
@Component({
  selector: 'app-fox-constellation',
  template: `
    <svg aria-hidden="true" viewBox="0 0 240 170" class="block h-auto w-full overflow-visible">
      <g fill="none" stroke="#e9f0c9" stroke-width="1" stroke-linejoin="round" opacity="0.5">
        <!-- Head outline, facing left: snout, forehead, two ears, neck, jaw. -->
        <polygon
          points="9,21 51,45 99,51 141,9 147,57 165,51 207,27 219,33 189,81 171,99 225,147 93,147 51,117 21,75 9,45"
        />
        <!-- The pale underside of the snout, and where the far ear meets the head. -->
        <polyline points="9,21 57,81 93,147" />
        <polyline points="147,57 171,99" />
      </g>
      <g fill="#e9f0c9">
        <circle cx="9" cy="21" r="3" />
        <circle cx="51" cy="45" r="1.6" />
        <circle cx="99" cy="51" r="1.8" />
        <circle cx="141" cy="9" r="3" />
        <circle cx="147" cy="57" r="1.8" />
        <circle cx="165" cy="51" r="1.4" />
        <circle cx="207" cy="27" r="2.6" />
        <circle cx="219" cy="33" r="1.4" />
        <circle cx="189" cy="81" r="1.6" />
        <circle cx="171" cy="99" r="1.8" />
        <circle cx="225" cy="147" r="2.2" />
        <circle cx="93" cy="147" r="2.2" />
        <circle cx="51" cy="117" r="1.6" />
        <circle cx="21" cy="75" r="1.6" />
        <circle cx="9" cy="45" r="1.8" />
        <circle cx="57" cy="81" r="1.4" />
      </g>
      <!-- The eye is the one warm star. -->
      <circle cx="105" cy="81" r="3.2" fill="#e9c46a" />
    </svg>
  `,
  host: { class: 'pointer-events-none block' },
})
export class FoxConstellation {}
