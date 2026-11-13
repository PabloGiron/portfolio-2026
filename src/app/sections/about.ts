import { Component, computed, signal } from '@angular/core';
import { ABOUT } from '../content';
import { SectionHeading } from '../shared/section-heading';
import { SpaceIcon } from '../shared/space-icon';

@Component({
  selector: 'app-about',
  imports: [SectionHeading, SpaceIcon],
  templateUrl: './about.html',
  host: { class: 'block' },
})
export class About {
  protected readonly about = ABOUT;

  /** How much of the frontend side is revealed, from 0 to 100. */
  protected readonly split = signal(50);

  /** Clips the frontend layer so only the part left of the divider shows. */
  protected readonly frontendClip = computed(() => `inset(0 ${100 - this.split()}% 0 0)`);

  protected readonly splitDescription = computed(
    () => `${this.split()}% frontend, ${100 - this.split()}% backend`,
  );

  protected onSplit(event: Event): void {
    this.split.set(Number((event.target as HTMLInputElement).value));
  }
}
