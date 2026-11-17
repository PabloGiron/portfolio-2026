import { Component } from '@angular/core';
import { PROFILE } from '../content';
import { FoxConstellation } from '../shared/fox-constellation';
import { MoonScene } from './moon-scene';

@Component({
  selector: 'app-hero',
  imports: [FoxConstellation, MoonScene],
  templateUrl: './hero.html',
  host: { class: 'block' },
})
export class Hero {
  protected readonly profile = PROFILE;
}
