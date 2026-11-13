import { Component } from '@angular/core';
import { PROFILE } from '../content';

@Component({
  selector: 'app-hero',
  templateUrl: './hero.html',
  host: { class: 'block' },
})
export class Hero {
  protected readonly profile = PROFILE;
}
