export interface RenderLoopClock {
  requestAnimationFrame(callback: FrameRequestCallback): number;
  cancelAnimationFrame(frameId: number): void;
}

export interface RenderFrame {
  frameIndex: number;
  timestamp: number;
  deltaMs: number;
  fps: number;
}

export type RenderFrameHandler = (frame: RenderFrame) => void;

export class RenderLoop {
  private frameId: number | null = null;
  private frameIndex = 0;
  private lastTimestamp: number | null = null;

  constructor(
    private readonly onFrame: RenderFrameHandler,
    private readonly clock: RenderLoopClock = window
  ) {}

  start(): void {
    if (this.frameId !== null) {
      return;
    }
    this.frameId = this.clock.requestAnimationFrame((timestamp) => this.tick(timestamp));
  }

  stop(): void {
    if (this.frameId !== null) {
      this.clock.cancelAnimationFrame(this.frameId);
    }
    this.frameId = null;
    this.frameIndex = 0;
    this.lastTimestamp = null;
  }

  private tick(timestamp: number): void {
    const deltaMs = this.lastTimestamp === null ? 16.67 : timestamp - this.lastTimestamp;
    this.lastTimestamp = timestamp;
    this.frameIndex += 1;
    this.onFrame({
      frameIndex: this.frameIndex,
      timestamp,
      deltaMs,
      fps: deltaMs <= 0 ? 60 : Math.min(60, 1000 / deltaMs)
    });
    this.frameId = this.clock.requestAnimationFrame((nextTimestamp) => this.tick(nextTimestamp));
  }
}
