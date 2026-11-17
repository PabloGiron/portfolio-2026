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
  name: 'Pablo Giron',
  role: 'Fullstack developer',
  level: 'Lv. 29',
  city: 'GT-09',
  tagline:
    'Fullstack developer. Out here, anything is possible — I build web pages with Angular, Spring Boot and Kubernetes.',
  email: 'you@example.com',
  cvUrl: '#',
  year: '[YEAR]',
} as const;

export const ABOUT = {
  bio: '[WHO YOU ARE, WHAT YOU DO TODAY, HOW YOU WORK AND WHAT YOU WANT NEXT.]',
  facts: [
    { label: 'Based in', value: 'GT-09' },
    { label: 'Experience', value: '5 years' },
    { label: 'Focus', value: 'Backend' },
  ] as readonly Fact[],
  frontend: {
    eyebrow: 'Boots on the surface',
    title: 'frontend',
    blurb: 'The one everybody watches live. I love building intuitive interfaces that make life easier.',
    tech: ['Angular', 'TypeScript', 'Three.js', 'HTML', 'CSS'],
  } as StackSide,
  backend: {
    eyebrow: 'Mission control, 03:00',
    title: 'backend',
    blurb:
      'The one who gets everybody home. REST APIs for high-volume transactions, role-based authentication, multithreaded jobs and Kubernetes clusters.',
    tech: ['Spring Boot', 'Spring Batch', 'Micronaut', 'Kubernetes'],
  } as StackSide,
  hobbies: [
    { name: '[HOBBY]', icon: 'planet' },
    { name: '[HOBBY]', icon: 'rocket' },
    { name: '[HOBBY]', icon: 'moon' },
    { name: '[HOBBY]', icon: 'star' },
  ] as readonly Hobby[],
} as const;

export const EXPERIENCE = {
  summary:
    'Software engineer from Guatemala. I started in backend with Java and Spring Boot, moved into DevOps running Kubernetes clusters, and now build banking apps end to end as a fullstack developer.',
  jobs: [
    {
      route: 'Route 03 · Current',
      period: '2025 – Present',
      title: 'Fullstack Developer',
      company: 'Byte SW',
      location: 'Guatemala',
      highlights: ['Built the backend and frontend of banking apps.'],
      tech: ['Micronaut', 'Kubernetes', 'Angular'],
      current: true,
    },
    {
      route: 'Route 02',
      period: '2023 – 2025',
      title: 'Backend & DevOps',
      company: 'Byte SW',
      location: 'Guatemala',
      highlights: ['Managed a Kubernetes cluster and built backend apps.'],
      tech: ['Spring Boot', 'Kubernetes', 'Docker', 'Spring Batch'],
    },
    {
      route: 'Route 01',
      period: '2022 – 2023',
      title: 'Backend Developer',
      company: 'Byte SW',
      location: 'Guatemala',
      highlights: ['My journey started as a backend developer with inventory and banking apps.'],
      tech: ['Spring Boot', 'Java'],
    },
  ] as readonly Job[],
  education: {
    period: '2015 – 2021',
    degree: 'Software Engineering',
    school: 'Rafael Landívar University',
    location: 'Guatemala',
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
