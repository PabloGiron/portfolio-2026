import { Component } from '@angular/core';
import { PROJECTS } from '../content';
import { Cloud } from '../shared/cloud';
import { SectionHeading } from '../shared/section-heading';
import { SpaceIcon } from '../shared/space-icon';

@Component({
  selector: 'app-projects',
  imports: [SectionHeading, SpaceIcon, Cloud],
  template: `
    <section
      id="projects"
      aria-labelledby="projects-title"
      class="sky-clouds relative overflow-hidden px-6 py-24 md:px-16"
    >
      <app-cloud class="absolute top-[120px] right-[5%] w-[260px] opacity-90" />
      <app-cloud class="absolute top-[52%] -left-[60px] w-[320px] opacity-90" />
      <app-cloud class="absolute right-[18%] bottom-3.5 w-[220px] opacity-90" />
      <div class="relative mx-auto flex max-w-[1312px] flex-col gap-12">
        <div class="flex flex-wrap items-end justify-between gap-6">
          <app-section-heading
            index="003"
            label="Projects"
            title="Selected projects"
            headingId="projects-title"
            altitude="3 km"
            [pill]="true"
          />
          <a
            [href]="projects.allUrl"
            class="inline-flex min-h-12 items-center rounded-lg bg-space px-[18px] font-semibold hover:text-sky"
            >All projects on GitHub</a
          >
        </div>

        <ul class="grid grid-cols-[repeat(auto-fit,minmax(min(300px,100%),1fr))] gap-6">
          @for (project of projects.items; track $index) {
            <li class="flex">
              <article
                class="flex w-full flex-col overflow-hidden rounded-[14px] border border-line bg-surface"
              >
                <div class="relative flex h-[220px] items-center justify-center" [class]="project.tone">
                  <app-space-icon [name]="project.icon" [size]="120" />
                  <span class="absolute top-3.5 left-4 font-pixel text-xs">{{ number($index) }}</span>
                </div>
                <div class="flex grow flex-col gap-3.5 p-6">
                  <h3 class="text-2xl font-bold">{{ project.name }}</h3>
                  <p class="leading-relaxed text-cream-dim">{{ project.description }}</p>
                  <ul class="flex flex-wrap gap-2 text-[13px] font-medium" aria-label="Technologies">
                    @for (tech of project.tech; track $index) {
                      <li class="rounded-md border border-line bg-space px-2.5 py-1.5">{{ tech }}</li>
                    }
                  </ul>
                  <p class="mt-auto flex gap-6 text-[15px] font-semibold">
                    <a
                      [href]="project.liveUrl"
                      class="py-3 underline underline-offset-4 hover:text-sky"
                      [attr.aria-label]="'Live site: ' + project.name"
                      >Live site</a
                    >
                    <a
                      [href]="project.sourceUrl"
                      class="py-3 underline underline-offset-4 hover:text-sky"
                      [attr.aria-label]="'Source code: ' + project.name"
                      >Source</a
                    >
                  </p>
                </div>
              </article>
            </li>
          }
        </ul>
      </div>
    </section>
  `,
  host: { class: 'block' },
})
export class Projects {
  protected readonly projects = PROJECTS;

  protected number(index: number): string {
    return `No. ${String(index + 1).padStart(3, '0')}`;
  }
}
