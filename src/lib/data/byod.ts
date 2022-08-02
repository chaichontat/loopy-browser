import { Sample, type SampleParams } from '$lib/data/sample';
import { get } from 'svelte/store';
import { samples } from '../store';

async function readFile<T extends object>(
  dirHandle: FileSystemDirectoryHandle,
  name: string,
  mode: 'url' | 'plain'
): Promise<T | string> {
  const file = await dirHandle.getFileHandle(name).then((fileHandle) => fileHandle.getFile());

  if (mode === 'plain') {
    return JSON.parse(await file.text()) as T;
  } else {
    return URL.createObjectURL(file);
  }
}

export async function byod() {
  if (!('showDirectoryPicker' in window)) {
    alert('This browser does not support the File System API. Use Chrome/Safari.');
    return;
  }

  // if (window.location.protocol == 'http:') {
  //   alert('File system access requires HTTPS.');
  //   return;
  // }

  const directoryHandle = await window.showDirectoryPicker();

  let sp: SampleParams;
  try {
    sp = (await readFile<SampleParams>(directoryHandle, 'sample.json', 'plain')) as SampleParams;
  } catch (e) {
    alert('Cannot find sample.json in the specified directory');
    return;
  }

  sp.handle = directoryHandle;
  const sample = new Sample(sp);
  // focus.set({ ...get(focus), sample: sample.name });
  samples.set({ ...get(samples), [sample.name]: sample });
  // for await  (const entry of directoryHandle.values()) {
  //   console.log(entry.kind, entry.name);
  // }
}
