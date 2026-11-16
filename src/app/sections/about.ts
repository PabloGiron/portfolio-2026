import { Component, computed, signal } from '@angular/core';
import { ABOUT } from '../content';
import { SectionHeading } from '../shared/section-heading';
import { SpaceIcon } from '../shared/space-icon';

/** How much of the image the pointed-at side takes up, in percent. */
const EXPANDED = 72;

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

  /** Keyboard: the hidden range input moves the divider with the arrow keys. */
  protected onSplit(event: Event): void {
    this.split.set(Number((event.target as HTMLInputElement).value));
  }

  /** Pointing at (or tapping) a half of the image expands that side. */
  protected onPointer(event: PointerEvent): void {
    const box = (event.currentTarget as HTMLElement).getBoundingClientRect();
    const overFrontend = event.clientX - box.left < box.width / 2;
    this.split.set(overFrontend ? EXPANDED : 100 - EXPANDED);
  }

  /** The mouse leaving puts the divider back in the middle; a tap stays where it is. */
  protected onLeave(event: PointerEvent): void {
    if (event.pointerType === 'mouse') {
      this.split.set(50);
    }
  }
}
