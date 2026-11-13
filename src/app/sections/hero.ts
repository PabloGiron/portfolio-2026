import { Component } from '@angular/core';
import { PROFILE } from '../content';
import { MoonScene } from './moon-scene';

@Component({
  selector: 'app-hero',
  imports: [MoonScene],
  templateUrl: './hero.html',
  host: { class: 'block' },
})
export class Hero {
  protected readonly profile = PROFILE;
}
