import { DOCUMENT } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { email, form, FormField, required, submit } from '@angular/forms/signals';
import { CONTACT, PROFILE } from '../content';

interface ContactMessage {
  name: string;
  email: string;
  message: string;
}

@Component({
  selector: 'app-contact',
  imports: [FormField],
  templateUrl: './contact.html',
  host: { class: 'block' },
})
export class Contact {
  private readonly document = inject(DOCUMENT);

  protected readonly contact = CONTACT;
  protected readonly profile = PROFILE;

  protected readonly message = signal<ContactMessage>({ name: '', email: '', message: '' });

  protected readonly contactForm = form(this.message, (path) => {
    required(path.name, { message: 'Enter your name.' });
    required(path.email, { message: 'Enter your email address.' });
    email(path.email, { message: 'Enter a valid email address, like name@example.com.' });
    required(path.message, { message: 'Write a short message.' });
  });

  /** True once the visitor's email app has been asked to open. */
  protected readonly handedOff = signal(false);

  /**
   * There is no server: a valid form opens the visitor's email app with the
   * message filled in, addressed to PROFILE.email.
   */
  protected async onSubmit(event: Event): Promise<void> {
    event.preventDefault();
    this.handedOff.set(false);
    await submit(this.contactForm, async () => {
      const { name, email: from, message } = this.message();
      const subject = encodeURIComponent(`Portfolio message from ${name}`);
      const body = encodeURIComponent(`${message}\n\n${name}\n${from}`);
      const view = this.document.defaultView;
      if (view) {
        view.location.href = `mailto:${this.profile.email}?subject=${subject}&body=${body}`;
      }
      this.handedOff.set(true);
      return undefined;
    });
  }
}
