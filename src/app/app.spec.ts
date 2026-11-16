import { TestBed } from '@angular/core/testing';
import { App } from './app';
import { PROFILE } from './content';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
    }).compileComponents();
  });

  function render(): HTMLElement {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    return fixture.nativeElement as HTMLElement;
  }

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should show the name as the only h1', () => {
    const headings = render().querySelectorAll('h1');
    expect(headings.length).toBe(1);
    expect(headings[0].textContent).toContain(PROFILE.name);
  });

  it('should render the five sections the nav links to', () => {
    const page = render();
    for (const id of ['top', 'about', 'experience', 'projects', 'contact']) {
      expect(page.querySelector(`section#${id}`), id).not.toBeNull();
    }
  });

  it('should order the sections as a descent from space to the ground', () => {
    const ids = Array.from(render().querySelectorAll('main > * > section')).map((s) => s.id);
    expect(ids).toEqual(['top', 'experience', 'about', 'projects', 'contact']);
  });

  it('should move the About divider when the slider changes', () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    const page = fixture.nativeElement as HTMLElement;
    const slider = page.querySelector<HTMLInputElement>('#about input[type="range"]')!;
    slider.value = '80';
    slider.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    expect(slider.getAttribute('aria-valuetext')).toBe('80% frontend, 20% backend');
  });

  it('should show validation messages when the contact form is submitted empty', async () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    const page = fixture.nativeElement as HTMLElement;
    page.querySelector<HTMLFormElement>('#contact form')!.dispatchEvent(
      new Event('submit', { cancelable: true }),
    );
    await fixture.whenStable();
    fixture.detectChanges();
    expect(page.querySelector('#contact-name-error')?.textContent).toContain('Enter your name.');
    expect(page.querySelector('#contact-email-error')).not.toBeNull();
    expect(page.querySelector('#contact-message-error')).not.toBeNull();
  });
});
