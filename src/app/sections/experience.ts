import { Component } from '@angular/core';
import { EXPERIENCE, PROFILE } from '../content';
import { SectionHeading } from '../shared/section-heading';

@Component({
  selector: 'app-experience',
  imports: [SectionHeading],
  template: `
    <section
      id="experience"
      aria-labelledby="experience-title"
      class="sky-orbit px-6 pt-24 pb-56 md:px-16"
    >
      <div class="mx-auto flex max-w-[1312px] flex-wrap gap-16">
        <div class="flex min-w-0 flex-[1_1_320px] flex-col gap-6">
          <app-section-heading
            index="001"
            label="Experience"
            altitude="400 km"
            title="The journey so far"
            headingId="experience-title"
          />
          <p class="text-lg leading-relaxed text-cream-dim">{{ experience.summary }}</p>
          <a
            [href]="profile.cvUrl"
            class="inline-flex min-h-12 items-center self-start rounded-lg border border-steel px-[22px] font-semibold hover:border-sky hover:text-sky"
            >Download CV</a
          >
        </div>

        <ol class="flex min-w-0 flex-[2_1_560px] flex-col">
          @for (job of experience.jobs; track job.route) {
            <li class="flex gap-6">
              <div class="flex w-7 flex-none flex-col items-center" aria-hidden="true">
                <svg width="28" height="28" viewBox="0 0 28 28">
                  @if (job.current) {
                    <circle cx="14" cy="14" r="8" fill="#e9f0c9" />
                    <g transform="rotate(-20 14 14)">
                      <ellipse cx="14" cy="14" rx="13" ry="3.5" fill="none" stroke="#9cc3d8" stroke-width="2" />
                    </g>
                  } @else {
                    <circle cx="14" cy="14" r="9" fill="#3b657a" stroke="#9cc3d8" stroke-width="2" />
                  }
                </svg>
                <div class="w-0 grow border-l-2 border-dashed border-steel"></div>
              </div>
              <article class="flex min-w-0 flex-1 flex-col gap-2.5 pb-10">
                <p class="flex flex-wrap justify-between gap-3 font-pixel text-xs text-muted">
                  <span [class.text-cream]="job.current">{{ job.route }}</span>
                  <span>{{ job.period }}</span>
                </p>
                <h3 class="text-2xl font-bold">{{ job.title }}</h3>
                <p class="font-medium text-cream-dim">{{ job.company }} · {{ job.location }}</p>
                @if (job.highlights.length > 0) {
                  <ul class="mt-1 flex list-disc flex-col gap-1.5 pl-5 leading-relaxed text-cream-dim">
                    @for (item of job.highlights; track $index) {
                      <li>{{ item }}</li>
                    }
                  </ul>
                }
                @if (job.tech.length > 0) {
                  <ul class="mt-1.5 flex flex-wrap gap-2 text-[13px] font-medium" aria-label="Technologies">
                    @for (tech of job.tech; track $index) {
                      <li class="rounded-md border border-steel bg-surface px-2.5 py-1.5">{{ tech }}</li>
                    }
                  </ul>
                }
              </article>
            </li>
          }
          <li class="flex gap-6">
            <div class="flex w-7 flex-none flex-col items-center" aria-hidden="true">
              <svg width="28" height="28" viewBox="0 0 28 28">
                <polygon points="14,1 17,11 27,14 17,17 14,27 11,17 1,14 11,11" fill="#e9c46a" />
              </svg>
            </div>
            <article class="flex min-w-0 flex-1 flex-col gap-2.5">
              <p class="flex flex-wrap justify-between gap-3 font-pixel text-xs text-muted">
                <span class="text-gold">Launch site</span>
                <span>{{ experience.education.period }}</span>
              </p>
              <h3 class="text-2xl font-bold">{{ experience.education.degree }}</h3>
              <p class="font-medium text-cream-dim">
                {{ experience.education.school }} · {{ experience.education.location }}
              </p>
            </article>
          </li>
        </ol>
      </div>
    </section>
  `,
  host: { class: 'block' },
})
export class Experience {
  protected readonly experience = EXPERIENCE;
  protected readonly profile = PROFILE;
}
