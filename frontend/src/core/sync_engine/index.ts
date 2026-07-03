export type ScheduledWork = () => void;

export interface FrameScheduler {
  schedule(work: ScheduledWork): void;
  cancel(): void;
}

export function createFrameScheduler(): FrameScheduler {
  let frameId: number | null = null;
  let pendingWork: ScheduledWork | null = null;

  return {
    schedule(work: ScheduledWork) {
      pendingWork = work;
      if (frameId !== null) {
        return;
      }
      frameId = requestAnimationFrame(() => {
        frameId = null;
        const next = pendingWork;
        pendingWork = null;
        next?.();
      });
    },
    cancel() {
      if (frameId !== null) {
        cancelAnimationFrame(frameId);
      }
      frameId = null;
      pendingWork = null;
    }
  };
}

export function createIntervalBatcher<T>(
  flushIntervalMs: number,
  onFlush: (items: readonly T[]) => void
): {
  push(item: T): void;
  flush(): void;
  close(): void;
} {
  let timerId: ReturnType<typeof setTimeout> | null = null;
  const buffer: T[] = [];

  function scheduleFlush(): void {
    if (timerId !== null) {
      return;
    }
    timerId = setTimeout(() => {
      timerId = null;
      flush();
    }, flushIntervalMs);
  }

  function flush(): void {
    if (timerId !== null) {
      clearTimeout(timerId);
      timerId = null;
    }
    if (buffer.length === 0) {
      return;
    }
    const items = buffer.splice(0, buffer.length);
    onFlush(items);
  }

  return {
    push(item: T) {
      buffer.push(item);
      scheduleFlush();
    },
    flush,
    close() {
      if (timerId !== null) {
        clearTimeout(timerId);
      }
      timerId = null;
      buffer.splice(0, buffer.length);
    }
  };
}
