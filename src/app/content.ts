/**
 * All the text shown on the site lives here.
 * Replace every [BRACKETED] placeholder with your own details.
 */

export type SpaceIconName = 'planet' | 'rocket' | 'moon' | 'star' | 'sun' | 'satellite';

export interface Fact {
  readonly label: string;
  readonly value: string;
}

export interface StackSide {
  readonly eyebrow: string;
  readonly title: string;
  readonly blurb: string;
  readonly tech: readonly string[];
}

export interface Hobby {
  readonly name: string;
  readonly icon: SpaceIconName;
}

export interface Job {
  readonly route: string;
  readonly period: string;
  readonly title: string;
  readonly company: string;
  readonly location: string;
  readonly highlights: readonly string[];
  readonly tech: readonly string[];
  readonly current?: boolean;
}

export interface Education {
  readonly period: string;
  readonly degree: string;
  readonly school: string;
  readonly location: string;
}

export interface Project {
  readonly name: string;
  readonly description: string;
  readonly tech: readonly string[];
  readonly liveUrl: string;
  readonly sourceUrl: string;
  readonly icon: SpaceIconName;
  /** Tailwind background class for the card's picture area. */
  readonly tone: string;
}

export interface SocialLink {
  readonly label: string;
  readonly url: string;
}

export const PROFILE = {
  name: '[YOUR NAME]',
  role: '[YOUR ROLE]',
  level: 'Lv. [XX]',
  city: '[YOUR CITY]',
  tagline:
    '[YOUR ROLE]. Out here, anything is possible — I build [WHAT YOU BUILD] with Angular and [YOUR STACK].',
  email: 'you@example.com',
  cvUrl: '#',
  year: '[YEAR]',
} as const;

export const ABOUT = {
  bio: '[WHO YOU ARE, WHAT YOU DO TODAY, HOW YOU WORK AND WHAT YOU WANT NEXT.]',
  facts: [
    { label: 'Based in', value: '[YOUR CITY]' },
    { label: 'Experience', value: '[X] years' },
    { label: 'Focus', value: '[YOUR FOCUS]' },
  ] as readonly Fact[],
  frontend: {
    eyebrow: 'Boots on the surface',
    title: 'frontend',
    blurb: 'The one everybody watches live. [WHAT YOU LOVE ABOUT BUILDING INTERFACES.]',
    tech: ['Angular', 'TypeScript', 'Three.js', '[TECH]', '[TECH]'],
  } as StackSide,
  backend: {
    eyebrow: 'Mission control, 03:00',
    title: 'backend',
    blurb: 'The one who gets everybody home. [WHAT YOU DO ON THE SERVER SIDE.]',
    tech: ['[TECH]', '[TECH]', '[TECH]', '[TECH]'],
  } as StackSide,
  hobbies: [
    { name: '[HOBBY]', icon: 'planet' },
    { name: '[HOBBY]', icon: 'rocket' },
    { name: '[HOBBY]', icon: 'moon' },
    { name: '[HOBBY]', icon: 'star' },
  ] as readonly Hobby[],
} as const;

export const EXPERIENCE = {
  summary: '[ONE OR TWO SENTENCES SUMMING UP YOUR CAREER PATH.]',
  jobs: [
    {
      route: 'Route 03 · Current',
      period: '[YEAR] – Present',
      title: '[JOB TITLE]',
      company: '[COMPANY]',
      location: '[LOCATION]',
      highlights: ['[WHAT YOU BUILT OR OWNED]', '[A RESULT YOU ARE PROUD OF]'],
      tech: ['Angular', '[TECH]', '[TECH]'],
      current: true,
    },
    {
      route: 'Route 02',
      period: '[YEAR] – [YEAR]',
      title: '[JOB TITLE]',
      company: '[COMPANY]',
      location: '[LOCATION]',
      highlights: ['[WHAT YOU BUILT OR OWNED]', '[A RESULT YOU ARE PROUD OF]'],
      tech: ['[TECH]', '[TECH]'],
    },
    {
      route: 'Route 01',
      period: '[YEAR] – [YEAR]',
      title: '[JOB TITLE]',
      company: '[COMPANY]',
      location: '[LOCATION]',
      highlights: ['[WHAT YOU BUILT OR OWNED]'],
      tech: [],
    },
  ] as readonly Job[],
  education: {
    period: '[YEAR] – [YEAR]',
    degree: '[DEGREE OR COURSE]',
    school: '[SCHOOL]',
    location: '[LOCATION]',
  } as Education,
} as const;

export const PROJECTS = {
  allUrl: '#',
  items: [
    {
      name: '[PROJECT NAME]',
      description: '[WHAT IT IS, THE PROBLEM IT SOLVES AND YOUR PART IN IT.]',
      tech: ['Angular', '[TECH]', '[TECH]'],
      liveUrl: '#',
      sourceUrl: '#',
      icon: 'planet',
      tone: 'bg-[#1a3f52]',
    },
    {
      name: '[PROJECT NAME]',
      description: '[WHAT IT IS, THE PROBLEM IT SOLVES AND YOUR PART IN IT.]',
      tech: ['[TECH]', '[TECH]'],
      liveUrl: '#',
      sourceUrl: '#',
      icon: 'sun',
      tone: 'bg-soil',
    },
    {
      name: '[PROJECT NAME]',
      description: '[WHAT IT IS, THE PROBLEM IT SOLVES AND YOUR PART IN IT.]',
      tech: ['[TECH]', '[TECH]'],
      liveUrl: '#',
      sourceUrl: '#',
      icon: 'satellite',
      tone: 'bg-[#0f2836]',
    },
  ] as readonly Project[],
} as const;

export const CONTACT = {
  pitch: "Have a role or a project in mind? Send a signal — I'm open to [WHAT YOU ARE OPEN TO].",
  links: [
    { label: 'LinkedIn', url: '#' },
    { label: 'GitHub', url: '#' },
  ] as readonly SocialLink[],
} as const;
