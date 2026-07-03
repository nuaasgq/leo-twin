const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..", "..");

const files = {
  app: read("frontend/src/app/App.tsx"),
  cesium: read("frontend/src/3d/cesium/CesiumGlobe.tsx"),
  satellites: read("frontend/src/3d/orbit_renderer/satelliteEntities.ts"),
  snapshot: read("frontend/src/state/snapshot_engine/index.ts"),
  reducer: read("frontend/src/state/reducer/index.ts"),
  throttle: read("frontend/src/stream/throttle_layer/index.ts"),
  renderLoop: read("frontend/src/render/render_loop/index.ts")
};

assert.match(files.app, /SnapshotEngine/);
assert.match(files.app, /EventThrottleLayer/);
assert.doesNotMatch(files.app, /useObservabilityState/);
assert.doesNotMatch(files.app, /new ObservabilityStore/);

assert.match(files.snapshot, /WorldSnapshot/);
assert.match(files.snapshot, /snapshotHz/);
assert.match(files.reducer, /satellites: Map<string, SatelliteState>/);
assert.match(files.reducer, /spatialCell/);
assert.match(files.throttle, /dropRedundantUpdates/);
assert.match(files.renderLoop, /requestAnimationFrame/);

assert.match(files.satellites, /PointPrimitiveCollection/);
assert.match(files.cesium, /RenderLoop/);
assert.match(files.cesium, /latestSnapshotRef/);
assert.doesNotMatch(files.satellites, /EntityCollection/);
assert.doesNotMatch(files.satellites, /entities\.add/);

console.log("frontend render performance architecture checks passed");

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}
