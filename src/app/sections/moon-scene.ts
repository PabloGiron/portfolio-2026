import { DOCUMENT } from '@angular/common';
import {
  afterNextRender,
  Component,
  DestroyRef,
  ElementRef,
  inject,
  input,
  signal,
  viewChild,
} from '@angular/core';
import type * as Three from 'three';

/**
 * Path of the Blender export for the hero, relative to the site root.
 * Leave as null to show the stand-in scene built in code below.
 * Once the model exists, save it as public/models/hero.glb and set this to
 * 'models/hero.glb'.
 */
export const HERO_MODEL_URL: string | null = null;

/** How far the scene may turn towards the pointer, in radians. */
const MAX_TURN = 0.45;
const MAX_TILT = 0.2;

const deg = (value: number): number => (value * Math.PI) / 180;

/**
 * The 3D scene on the main page: a person resting in a crescent moon.
 * Whatever is placed inside <app-moon-scene> is shown instead when 3D cannot
 * run (reduced motion, no WebGL, or before the scene has loaded).
 */
@Component({
  selector: 'app-moon-scene',
  template: `
    <canvas #canvas aria-hidden="true" class="block size-full" [class.hidden]="!live()"></canvas>
    @if (!live()) {
      <ng-content />
    }
  `,
  host: {
    class: 'block aspect-[400/420] w-full max-w-[480px] touch-pan-y',
    role: 'img',
    '[attr.aria-label]': 'label()',
    '(pointermove)': 'onPointerMove($event)',
    '(pointerleave)': 'onPointerLeave()',
  },
})
export class MoonScene {
  readonly label = input.required<string>();

  protected readonly live = signal(false);

  private readonly host = inject<ElementRef<HTMLElement>>(ElementRef);
  private readonly canvas = viewChild.required<ElementRef<HTMLCanvasElement>>('canvas');
  private readonly document = inject(DOCUMENT);
  private readonly destroyRef = inject(DestroyRef);

  /** Pointer position over the scene, each axis from -1 to 1. */
  private readonly pointer = { x: 0, y: 0 };
  private destroyed = false;

  constructor() {
    this.destroyRef.onDestroy(() => (this.destroyed = true));
    afterNextRender(() => void this.start());
  }

  protected onPointerMove(event: PointerEvent): void {
    const box = this.host.nativeElement.getBoundingClientRect();
    if (box.width === 0 || box.height === 0) {
      return;
    }
    this.pointer.x = Math.max(-1, Math.min(1, ((event.clientX - box.left) / box.width) * 2 - 1));
    this.pointer.y = Math.max(-1, Math.min(1, ((event.clientY - box.top) / box.height) * 2 - 1));
  }

  protected onPointerLeave(): void {
    this.pointer.x = 0;
    this.pointer.y = 0;
  }

  private async start(): Promise<void> {
    const view = this.document.defaultView;
    if (!view || typeof view.matchMedia !== 'function') {
      return;
    }
    if (view.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }

    // Three.js is loaded only here, so it never weighs on the first paint.
    const THREE = await import('three');
    if (this.destroyed) {
      return;
    }

    let renderer: Three.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({
        canvas: this.canvas().nativeElement,
        alpha: true,
        antialias: true,
      });
    } catch {
      return; // No WebGL: the fallback stays on screen.
    }
    renderer.setPixelRatio(Math.min(view.devicePixelRatio || 1, 2));

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(32, 400 / 420, 0.1, 50);
    camera.position.set(0, 0, 7.6);

    scene.add(new THREE.HemisphereLight(0xe9f0c9, 0x142026, 1.3));
    const sun = new THREE.DirectionalLight(0xffffff, 1.7);
    sun.position.set(-2.5, 3, 4);
    scene.add(sun);

    const stage = new THREE.Group();
    scene.add(stage);

    let standIn: StandIn | null = null;
    const model = HERO_MODEL_URL ? await this.loadModel(THREE, HERO_MODEL_URL) : null;
    if (this.destroyed) {
      renderer.dispose();
      return;
    }
    if (model) {
      stage.add(model);
    } else {
      standIn = buildStandIn(THREE);
      stage.add(standIn.root);
    }

    this.live.set(true);

    const host = this.host.nativeElement;
    const resize = (): void => {
      const width = host.clientWidth;
      const height = host.clientHeight;
      if (width === 0 || height === 0) {
        return;
      }
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(host);

    // Stop drawing while the scene is scrolled out of view.
    let visible = true;
    const visibilityObserver = new IntersectionObserver((entries) => {
      visible = entries.some((entry) => entry.isIntersecting);
    });
    visibilityObserver.observe(host);

    const clock = new THREE.Clock();
    let frame = 0;
    const draw = (): void => {
      frame = view.requestAnimationFrame(draw);
      if (!visible) {
        return;
      }
      const time = clock.getElapsedTime();

      // The visitor can nudge the scene, but only within a small range.
      stage.rotation.y += (this.pointer.x * MAX_TURN - stage.rotation.y) * 0.06;
      stage.rotation.x += (this.pointer.y * MAX_TILT - stage.rotation.x) * 0.06;
      stage.position.y = Math.sin(time * 0.6) * 0.06;

      standIn?.animate(time);
      renderer.render(scene, camera);
    };
    // The canvas only gets a size once the fallback is gone, so wait a frame.
    view.requestAnimationFrame(() => {
      resize();
      draw();
    });

    this.destroyRef.onDestroy(() => {
      view.cancelAnimationFrame(frame);
      resizeObserver.disconnect();
      visibilityObserver.disconnect();
      scene.traverse((object) => {
        const mesh = object as Three.Mesh;
        mesh.geometry?.dispose();
        const material = mesh.material;
        if (Array.isArray(material)) {
          material.forEach((item) => item.dispose());
        } else {
          material?.dispose();
        }
      });
      renderer.dispose();
    });
  }

  /** Loads the Blender export. Returns null if it is missing or broken. */
  private async loadModel(THREE: typeof Three, url: string): Promise<Three.Object3D | null> {
    try {
      const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
      const gltf = await new GLTFLoader().loadAsync(url);
      // Scale and centre whatever was exported so it fills the same space
      // as the stand-in, regardless of the units used in Blender.
      const box = new THREE.Box3().setFromObject(gltf.scene);
      const size = box.getSize(new THREE.Vector3());
      const centre = box.getCenter(new THREE.Vector3());
      const scale = 3.4 / Math.max(size.x, size.y, size.z, 0.001);
      gltf.scene.position.sub(centre).multiplyScalar(scale);
      gltf.scene.scale.setScalar(scale);
      const holder = new THREE.Group();
      holder.add(gltf.scene);
      return holder;
    } catch {
      return null;
    }
  }
}

interface StandIn {
  readonly root: Three.Group;
  animate(time: number): void;
}

/**
 * Low-poly stand-in built from simple shapes, laid out like the original
 * drawing. It is replaced by the Blender model once HERO_MODEL_URL is set.
 */
function buildStandIn(THREE: typeof Three): StandIn {
  const root = new THREE.Group();
  const flat = (color: number): Three.MeshStandardMaterial =>
    new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.9 });

  // Crescent moon: an outer circle with an offset circle cut out of it.
  const outline = new THREE.Shape();
  outline.absarc(0, 0, 1.6, deg(74.1), deg(-164.1), true);
  outline.absarc(-0.5, 0.5, 1.4, deg(-137.9), deg(47.9), false);
  const moonGeometry = new THREE.ExtrudeGeometry(outline, {
    depth: 0.5,
    bevelEnabled: true,
    bevelThickness: 0.08,
    bevelSize: 0.08,
    bevelSegments: 2,
    curveSegments: 40,
  });
  moonGeometry.translate(0, 0, -0.25);
  root.add(new THREE.Mesh(moonGeometry, flat(0xe9f0c9)));

  const craters: ReadonlyArray<readonly [number, number, number]> = [
    [1.0, -0.9, 0.1],
    [1.3, -0.2, 0.06],
    [0.5, -1.35, 0.07],
  ];
  for (const [x, y, radius] of craters) {
    const crater = new THREE.Mesh(new THREE.CircleGeometry(radius, 12), flat(0xc8d3bd));
    crater.position.set(x, y, 0.335);
    root.add(crater);
  }

  // The person: capsules joined end to end, lying back in the curve.
  const figure = new THREE.Group();
  const up = new THREE.Vector3(0, 1, 0);
  const limb = (
    from: readonly [number, number],
    to: readonly [number, number],
    radius: number,
    color: number,
    z = 0,
  ): Three.Mesh => {
    const start = new THREE.Vector3(from[0], from[1], z);
    const end = new THREE.Vector3(to[0], to[1], z);
    const direction = end.clone().sub(start);
    const mesh = new THREE.Mesh(
      new THREE.CapsuleGeometry(radius, direction.length(), 3, 8),
      flat(color),
    );
    mesh.position.copy(start).add(end).multiplyScalar(0.5);
    mesh.quaternion.setFromUnitVectors(up, direction.normalize());
    figure.add(mesh);
    return mesh;
  };

  const hips = [0.05, -0.73] as const;
  const torso = limb(hips, [0.5, -0.2], 0.17, 0x5b8aa3);
  limb([0.48, -0.18], [0.82, 0.06], 0.07, 0x4a7890, -0.08); // upper arm, behind the head
  limb([0.82, 0.06], [0.66, 0.12], 0.06, 0x4a7890, -0.08); // forearm
  limb(hips, [-0.34, -0.24], 0.11, 0x3b657a, 0.08); // raised thigh
  limb([-0.34, -0.24], [-0.56, -0.87], 0.09, 0x3b657a, 0.08); // shin
  limb(hips, [-0.34, -0.6], 0.11, 0x2c5166, -0.08); // resting thigh
  limb([-0.34, -0.6], [-0.83, -0.82], 0.09, 0x2c5166, -0.08); // resting shin

  const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.17, 1), flat(0xc8d3bd));
  head.position.set(0.62, 0.02, 0);
  figure.add(head);
  root.add(figure);

  // The thought: two small dots rising to a star.
  for (const [x, y, size] of [
    [0.36, 0.34, 0.05],
    [0.22, 0.52, 0.07],
  ] as const) {
    const dot = new THREE.Mesh(new THREE.BoxGeometry(size, size, size), flat(0x9cc3d8));
    dot.position.set(x, y, 0);
    root.add(dot);
  }
  const star = new THREE.Mesh(new THREE.OctahedronGeometry(0.2, 0), flat(0xe9c46a));
  star.position.set(-0.04, 0.84, 0);
  star.scale.set(1, 1, 0.5);
  root.add(star);

  // Background: a small ringed planet and a comet.
  const planet = new THREE.Group();
  planet.add(new THREE.Mesh(new THREE.IcosahedronGeometry(0.2, 1), flat(0x3b657a)));
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.34, 0.015, 6, 40), flat(0x9cc3d8));
  ring.rotation.x = deg(72);
  planet.add(ring);
  planet.position.set(-1.36, 1.26, -0.6);
  planet.rotation.z = deg(18);
  root.add(planet);

  const comet = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.1, 0.1), flat(0xe9f0c9));
  comet.position.set(1.5, 1.42, -0.4);
  root.add(comet);
  const tail = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.55, 5), flat(0x9cc3d8));
  tail.position.set(1.26, 1.56, -0.4);
  tail.rotation.z = deg(60);
  root.add(tail);

  return {
    root,
    animate(time: number): void {
      star.rotation.y = time * 0.8;
      star.position.y = 0.84 + Math.sin(time * 1.4) * 0.03;
      planet.rotation.y = time * 0.25;
      // Slow breathing.
      const breath = 1 + Math.sin(time * 1.1) * 0.03;
      torso.scale.set(breath, 1, breath);
    },
  };
}
