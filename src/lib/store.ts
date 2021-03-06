import sampleList from '$lib/data/meh';
import { get, writable, type Writable } from 'svelte/store';
import type { NameWithFeature } from './data/features';
import type { Sample } from './data/sample';

export type Idx = { idx: number | null; source: string };

export type State = {
  lockedIdx: Idx;
  currIdx: Idx;
  readonly locked: boolean;
};

export const store: Writable<State> = writable({
  lockedIdx: { idx: -1, source: 'scatter' },
  currIdx: { idx: 0, source: 'scatter' },
  get locked() {
    return this.lockedIdx.idx !== -1;
  }
});

// Samples
export const samples: Writable<Record<string, Sample>> = writable({});
// Changed in mapTile and byod.
// Automatically hydrates on change.
export const activeSample: Writable<string> = writable('');
activeSample.subscribe((n) => {
  const s = get(samples)[n];
  if (!s) return;
  if (!s.hydrated) s.hydrate().catch(console.error);
  sample.set(s);
});
export const sample: Writable<Sample | undefined> = writable();

// Overlays and Features
type OverlayName = string;
export const activeFeatures: Writable<Record<OverlayName, NameWithFeature>> = writable({});
export const activeOverlay: Writable<string> = writable('');
export const annotating: Writable<{
  curr: string;
  keys: string[];
  spots?: string;
  show: boolean;
}> = writable({
  curr: '',
  keys: [],
  show: true
});

// Maps
export const activeMap: Writable<number> = writable(0);
export const mapList: Writable<number[]> = writable([]);
export function preload() {
  if (sampleList) {
    sampleList
      .then((ss) => {
        const obj = Object.fromEntries(ss.map((s) => [s.name, s]));
        samples.set({ ...obj, ...get(samples) });
      })
      .catch(console.error);
  }
}
