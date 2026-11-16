import { Component } from '@angular/core';

/**
 * The office the page lands in, drawn along the bottom of the "Let's talk"
 * section. The wall behind it is that section's background colour.
 *
 * TEMPORARY MOCK: this is a placeholder drawing. Replace the <svg> with the
 * real office artwork when it is ready.
 */
@Component({
  selector: 'app-office-scene',
  template: `
    <svg
      role="img"
      aria-label="Placeholder drawing of a home office: a desk with a monitor and an astronaut helmet resting on it, a chair, a shelf, a plant and two windows showing the sky."
      viewBox="0 90 1440 270"
      preserveAspectRatio="xMidYMax slice"
      class="block h-[200px] w-full md:h-[270px]"
    >
      <!-- Floor and rug (the wall is the section background) -->
      <rect x="0" y="290" width="1440" height="70" fill="#5a3d24" />
      <rect x="0" y="286" width="1440" height="6" fill="#20130a" />
      <ellipse cx="720" cy="326" rx="270" ry="16" fill="#3b657a" opacity="0.6" />

      <!-- Windows showing the sky outside -->
      <rect x="170" y="104" width="200" height="124" fill="#9ccbe0" stroke="#e9f0c9" stroke-width="6" />
      <line x1="270" y1="104" x2="270" y2="228" stroke="#e9f0c9" stroke-width="4" />
      <line x1="170" y1="166" x2="370" y2="166" stroke="#e9f0c9" stroke-width="4" />
      <polygon points="196,150 210,134 232,130 246,142 262,150" fill="#f4f7ea" />
      <rect x="1090" y="104" width="200" height="124" fill="#9ccbe0" stroke="#e9f0c9" stroke-width="6" />
      <line x1="1190" y1="104" x2="1190" y2="228" stroke="#e9f0c9" stroke-width="4" />
      <line x1="1090" y1="166" x2="1290" y2="166" stroke="#e9f0c9" stroke-width="4" />
      <polygon points="1206,206 1222,190 1246,188 1260,200 1274,206" fill="#f4f7ea" />

      <!-- Poster of the moon from the main page -->
      <rect x="436" y="104" width="76" height="96" fill="#123142" stroke="#e9f0c9" stroke-width="3" />
      <path d="M486,126 A26,26 0 1 1 458,172 A22,22 0 1 0 486,126 Z" fill="#e9f0c9" />

      <!-- Chair -->
      <rect x="452" y="204" width="14" height="72" fill="#3b657a" />
      <rect x="452" y="264" width="74" height="12" fill="#3b657a" />
      <rect x="456" y="276" width="8" height="14" fill="#142026" />
      <rect x="514" y="276" width="8" height="14" fill="#142026" />

      <!-- Desk -->
      <rect x="548" y="214" width="400" height="14" fill="#b8923a" />
      <rect x="560" y="228" width="12" height="62" fill="#8a6a2a" />
      <rect x="924" y="228" width="12" height="62" fill="#8a6a2a" />
      <rect x="828" y="228" width="96" height="62" fill="#a07a30" />
      <rect x="866" y="254" width="20" height="5" fill="#20130a" />

      <!-- Monitor with a few lines of code -->
      <rect x="672" y="112" width="168" height="88" fill="#142026" stroke="#e9f0c9" stroke-width="4" />
      <rect x="688" y="128" width="64" height="6" fill="#9cc3d8" />
      <rect x="700" y="144" width="96" height="6" fill="#e9c46a" />
      <rect x="700" y="160" width="52" height="6" fill="#e9f0c9" />
      <rect x="688" y="176" width="80" height="6" fill="#9cc3d8" />
      <rect x="748" y="200" width="16" height="10" fill="#142026" />
      <rect x="726" y="208" width="60" height="6" fill="#142026" />

      <!-- Helmet left on the desk after the landing -->
      <circle cx="610" cy="190" r="24" fill="#e9f0c9" stroke="#142026" stroke-width="3" />
      <ellipse cx="604" cy="190" rx="14" ry="13" fill="#123142" />

      <!-- Mug and lamp -->
      <rect x="868" y="196" width="16" height="18" fill="#e9f0c9" />
      <circle cx="888" cy="205" r="6" fill="none" stroke="#e9f0c9" stroke-width="3" />
      <line x1="920" y1="214" x2="920" y2="168" stroke="#142026" stroke-width="4" />
      <polygon points="900,168 940,168 932,146 908,146" fill="#e9c46a" />

      <!-- Shelf with books -->
      <rect x="960" y="150" width="104" height="8" fill="#c8d3bd" />
      <rect x="968" y="118" width="12" height="32" fill="#e06a5a" />
      <rect x="982" y="124" width="10" height="26" fill="#e9c46a" />
      <rect x="994" y="114" width="14" height="36" fill="#9cc3d8" />
      <rect x="1010" y="126" width="10" height="24" fill="#e9f0c9" />
      <polygon points="1040,150 1048,126 1056,150" fill="#e9f0c9" />

      <!-- Plant -->
      <polygon points="1004,252 1044,252 1038,290 1010,290" fill="#e06a5a" />
      <polygon points="1024,252 1006,214 1022,226" fill="#5f8f5a" />
      <polygon points="1024,252 1028,200 1036,224" fill="#7aa86a" />
      <polygon points="1024,252 1048,216 1040,236" fill="#5f8f5a" />
    </svg>
  `,
  host: { class: 'block' },
})
export class OfficeScene {}
