/**
 * All the text shown on the site lives here.
 * Replace every [BRACKETED] placeholder with your own details.
 */

export type SpaceIconName =
  | 'planet'
  | 'rocket'
  | 'moon'
  | 'star'
  | 'sun'
  | 'satellite'
  | 'gamepad'
  | 'shoe'
  | 'book'
  | 'dumbbell'
  | 'webpage'
  | 'phone'
  | 'cart';

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
  /** Left out when the project has no public site; the card then shows only the source link. */
  readonly liveUrl?: string;
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
  name: 'Pablo Girón',
  role: 'Fullstack developer',
  level: 'Lv. 29',
  city: 'GT-09',
  tagline:
    'Fullstack developer. I build web pages with Angular and Spring Boot, and I can also manage Kubernetes clusters.',
  email: 'p4blogiron@gmail.com',
  cvUrl: '#',
  year: String(new Date().getFullYear()),
} as const;

export const ABOUT = {
  bio: "Hi, I'm Pablo. I've been working as a software developer for over 5 years. I like working closely with my team, learning from others and passing on what I know. I'm always up for the challenge of a new project.",
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
    { name: 'Video games', icon: 'gamepad' },
    { name: 'Running', icon: 'shoe' },
    { name: 'Reading', icon: 'book' },
    { name: 'Gym', icon: 'dumbbell' },
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
  allUrl: 'https://github.com/PabloGiron',
  items: [
    {
      name: 'First portfolio',
      description:
        'My first portfolio, designed and built from scratch with React and Sass: an intro, my skills, projects and hobbies on a single page. Its fox logo now lives in the stars at the top of this one.',
      tech: ['React', 'Sass', 'Material UI'],
      liveUrl: 'https://pablogiron.github.io/portfolio/',
      sourceUrl: 'https://github.com/PabloGiron/portfolio',
      icon: 'webpage',
      tone: 'bg-[#0f2836]',
    },
    {
      name: 'Paladins App',
      description:
        "A mobile app that shows a summary of a Paladins player's profile, built with Flutter on top of the game's API.",
      tech: ['Flutter', 'Dart', 'Provider'],
      sourceUrl: 'https://github.com/PabloGiron/paladins_app',
      icon: 'phone',
      tone: 'bg-[#1a3f52]',
    },
    {
      name: 'Pro-tech Web',
      description:
        'An e-commerce website built as a team of eight: an Angular storefront on top of a Node.js backend.',
      tech: ['Angular', 'Node.js', 'TypeScript'],
      sourceUrl: 'https://github.com/edvinfelipe/paginaweb',
      icon: 'cart',
      tone: 'bg-soil',
    },
  ] as readonly Project[],
} as const;

export const CONTACT = {
  pitch: "Have a role or a project in mind? Send a signal — I'm open to building your next web page.",
  links: [
    {
      label: 'LinkedIn',
      url: 'https://www.linkedin.com/in/juan-pablo-gir%C3%B3n-l%C3%B3pez-7362b2224/',
    },
    { label: 'GitHub', url: 'https://github.com/PabloGiron' },
  ] as readonly SocialLink[],
} as const;
