#!/usr/bin/env node
import { createRequire } from "node:module";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);

const HELP = `LEO-Twin browser acceptance smoke.

Usage:
  node scripts/smoke_browser_acceptance.mjs [options]

Options:
  --frontend-url <url>      Frontend console URL. Default: http://127.0.0.1:5173
  --backend-url <url>       Backend URL. Default: http://127.0.0.1:8765
  --timeout-seconds <n>     Wait timeout. Default: 90
  --browser-channel <name>  Playwright Chromium channel, for example chrome or msedge.
  --headed                  Show the browser window.
  --json                    Print machine-readable JSON summary.
  --help                    Show this help.

This smoke clicks the real frontend Initialize and Start buttons, verifies
backend runtime status movement, opens the dashboard surface, and resets the
runtime through the browser UI before exit. It does not replay events or
modify Event Kernel behavior.`;

const LABELS = {
  consoleHeading: /\u661f\u5ea7\u8fd0\u884c\u89c6\u56fe/u,
  dashboardRegion: /\u72ec\u7acb\u6570\u636e\u6001\u52bf\u9762\u677f/u,
  syncRegion: /\u524d\u7aef\u8fd0\u884c\u540c\u6b65\u72b6\u6001/u,
  initialize: /^\u521d\u59cb\u5316$/u,
  start: /^\u5f00\u59cb$/u,
  stop: /^\u505c\u6b62$/u,
  reset: /^\u91cd\u7f6e$/u
};

function parseArgs(argv) {
  const options = {
    frontendUrl: "http://127.0.0.1:5173",
    backendUrl: "http://127.0.0.1:8765",
    timeoutSeconds: 90,
    browserChannel: "",
    headed: false,
    json: false,
    help: false
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    switch (arg) {
      case "--frontend-url":
        options.frontendUrl = requiredValue(argv, ++index, arg);
        break;
      case "--backend-url":
        options.backendUrl = requiredValue(argv, ++index, arg);
        break;
      case "--timeout-seconds":
        options.timeoutSeconds = Number(requiredValue(argv, ++index, arg));
        if (!Number.isFinite(options.timeoutSeconds) || options.timeoutSeconds <= 0) {
          throw new Error("--timeout-seconds must be a positive number");
        }
        break;
      case "--browser-channel":
        options.browserChannel = requiredValue(argv, ++index, arg);
        break;
      case "--headed":
        options.headed = true;
        break;
      case "--json":
        options.json = true;
        break;
      case "--help":
      case "-h":
        options.help = true;
        break;
      default:
        throw new Error(`Unknown argument: ${arg}`);
    }
  }
  return options;
}

function requiredValue(argv, index, flag) {
  const value = argv[index];
  if (value === undefined || value.startsWith("--")) {
    throw new Error(`${flag} requires a value`);
  }
  return value;
}

function candidateModulePaths() {
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const repoRoot = path.resolve(scriptDir, "..");
  const frontendRoot = path.join(repoRoot, "frontend");
  const paths = [
    process.cwd(),
    repoRoot,
    frontendRoot,
    path.join(frontendRoot, "node_modules"),
    path.join(path.dirname(process.execPath), "..", "node_modules")
  ];
  const nodePath = process.env.NODE_PATH ?? "";
  for (const entry of nodePath.split(path.delimiter)) {
    if (entry.trim().length > 0) {
      paths.push(entry.trim());
    }
  }
  return Array.from(new Set(paths.map((entry) => path.resolve(entry))));
}

function loadPlaywright() {
  let lastError = null;
  for (const packageName of ["playwright-core", "playwright"]) {
    for (const basePath of candidateModulePaths()) {
      try {
        const resolved = require.resolve(packageName, { paths: [basePath] });
        return { module: require(resolved), resolved };
      } catch (error) {
        lastError = error;
      }
    }
  }
  const detail = lastError instanceof Error ? lastError.message : String(lastError);
  throw new Error(
    "Could not resolve the 'playwright-core' or 'playwright' package. Install it for the current " +
      "Node runtime or run through the bundled Codex dependency runtime. " +
      `Last resolver error: ${detail}`
  );
}

async function launchBrowser(chromium, options) {
  const candidates = options.browserChannel
    ? [options.browserChannel]
    : ["chrome", "msedge", "chromium"];
  const errors = [];
  for (const channel of candidates) {
    try {
      const launchOptions = {
        headless: !options.headed
      };
      if (channel !== "chromium") {
        launchOptions.channel = channel;
      }
      const browser = await chromium.launch(launchOptions);
      return { browser, channel };
    } catch (error) {
      errors.push(`${channel}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  throw new Error(`Unable to launch Chromium browser. Tried: ${errors.join(" | ")}`);
}

async function fetchRuntimeStatus(backendUrl) {
  const response = await fetch(`${backendUrl.replace(/\/$/, "")}/runtime/status`);
  if (!response.ok) {
    throw new Error(`runtime status HTTP ${response.status}`);
  }
  const payload = await response.json();
  return normalizeRuntimeStatus(payload);
}

function normalizeRuntimeStatus(payload) {
  const status = payload?.status ?? payload;
  if (typeof status !== "object" || status === null) {
    throw new Error("runtime status payload does not contain an object status");
  }
  return status;
}

async function waitForStatus(backendUrl, description, predicate, timeoutMs) {
  const startedAt = Date.now();
  let lastStatus = null;
  let lastError = null;
  while (Date.now() - startedAt < timeoutMs) {
    try {
      lastStatus = await fetchRuntimeStatus(backendUrl);
      lastError = null;
      if (predicate(lastStatus)) {
        return lastStatus;
      }
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
    }
    await sleep(250);
  }
  const errorDetail = lastError === null ? "" : ` Last error: ${lastError}.`;
  throw new Error(
    `Timed out waiting for ${description}.${errorDetail} Last status: ${JSON.stringify(
      runtimeStatusSummary(lastStatus)
    )}`
  );
}

async function waitForButtonEnabled(page, name, timeoutMs) {
  const locator = page.getByRole("button", { name });
  await locator.waitFor({ state: "visible", timeout: timeoutMs });
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    if (await locator.isEnabled()) {
      return locator;
    }
    await sleep(100);
  }
  throw new Error(`Timed out waiting for button to become enabled: ${String(name)}`);
}

async function clickButton(page, name, timeoutMs) {
  const locator = await waitForButtonEnabled(page, name, timeoutMs);
  await locator.click({ timeout: timeoutMs });
  return locator;
}

function simTime(status) {
  const value = Number(status.current_sim_time ?? status.sim_time ?? 0);
  return Number.isFinite(value) ? value : 0;
}

function runtimeStatusSummary(status) {
  if (typeof status !== "object" || status === null) {
    return null;
  }
  return {
    status: status.status,
    lifecycle_state: status.lifecycle_state,
    initialized: status.initialized,
    last_action: status.last_action,
    current_sim_time: status.current_sim_time,
    processed_event_count: status.processed_event_count,
    queued_event_count: status.queued_event_count,
    config_version: status.config_version,
    last_error: status.last_error ?? null
  };
}

function actionNotPending(status) {
  return !String(status.last_action ?? "").endsWith("_PENDING");
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function dashboardUrl(frontendUrl) {
  return `${frontendUrl.replace(/\/$/, "")}/dashboard`;
}

async function runSmoke(options) {
  const timeoutMs = Math.floor(options.timeoutSeconds * 1000);
  await waitForStatus(options.backendUrl, "backend runtime status availability", () => true, timeoutMs);
  const { module: playwright, resolved } = loadPlaywright();
  const { browser, channel } = await launchBrowser(playwright.chromium, options);
  const pageErrors = [];
  const summary = {
    ok: false,
    frontend_url: options.frontendUrl,
    dashboard_url: dashboardUrl(options.frontendUrl),
    backend_url: options.backendUrl,
    browser_channel: channel,
    playwright_module: resolved,
    initial_status: null,
    initialized_status: null,
    running_status: null,
    dashboard_visible: false,
    final_status: null,
    page_errors: pageErrors
  };
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 920 } });
    page.on("pageerror", (error) => {
      pageErrors.push(error.message);
    });

    summary.initial_status = runtimeStatusSummary(await fetchRuntimeStatus(options.backendUrl));
    await page.goto(options.frontendUrl, {
      waitUntil: "domcontentloaded",
      timeout: timeoutMs
    });
    await page.getByRole("heading", { name: LABELS.consoleHeading }).waitFor({
      state: "visible",
      timeout: timeoutMs
    });

    await clickButton(page, LABELS.reset, timeoutMs);
    await waitForStatus(
      options.backendUrl,
      "runtime reset through browser UI",
      (status) => actionNotPending(status) && status.initialized === false,
      timeoutMs
    );

    await clickButton(page, LABELS.initialize, timeoutMs);
    summary.initialized_status = runtimeStatusSummary(await waitForStatus(
      options.backendUrl,
      "runtime initialized through browser UI",
      (status) => actionNotPending(status) && status.initialized === true,
      timeoutMs
    ));

    await clickButton(page, LABELS.start, timeoutMs);
    summary.running_status = runtimeStatusSummary(await waitForStatus(
      options.backendUrl,
      "runtime sim time advancement after browser Start click",
      (status) =>
        actionNotPending(status) &&
        ["RUNNING", "COMPLETED"].includes(String(status.status)) &&
        simTime(status) > 0,
      timeoutMs
    ));

    await page.goto(dashboardUrl(options.frontendUrl), {
      waitUntil: "domcontentloaded",
      timeout: timeoutMs
    });
    await page.getByLabel(LABELS.dashboardRegion).waitFor({
      state: "visible",
      timeout: timeoutMs
    });
    await page.getByLabel(LABELS.syncRegion).waitFor({
      state: "visible",
      timeout: timeoutMs
    });
    summary.dashboard_visible = true;

    await page.goto(options.frontendUrl, {
      waitUntil: "domcontentloaded",
      timeout: timeoutMs
    });
    await page.getByRole("heading", { name: LABELS.consoleHeading }).waitFor({
      state: "visible",
      timeout: timeoutMs
    });
    await clickButton(page, LABELS.stop, timeoutMs);
    await waitForStatus(
      options.backendUrl,
      "runtime stopped through browser UI",
      (status) => actionNotPending(status) && String(status.status) === "STOPPED",
      timeoutMs
    );
    await clickButton(page, LABELS.reset, timeoutMs);
    summary.final_status = runtimeStatusSummary(await waitForStatus(
      options.backendUrl,
      "runtime reset after browser smoke",
      (status) => actionNotPending(status) && status.initialized === false,
      timeoutMs
    ));

    if (pageErrors.length > 0) {
      throw new Error(`Browser page errors were reported: ${pageErrors.join(" | ")}`);
    }
    summary.ok = true;
    return summary;
  } finally {
    await browser.close();
  }
}

function printSummary(summary, json) {
  if (json) {
    console.log(JSON.stringify(summary, null, 2));
    return;
  }
  console.log("Browser acceptance smoke passed.");
  console.log(`  console: ${summary.frontend_url}`);
  console.log(`  dashboard: ${summary.dashboard_url}`);
  console.log(`  backend: ${summary.backend_url}`);
  console.log(`  browser channel: ${summary.browser_channel}`);
  console.log(`  running sim time: ${simTime(summary.running_status)}`);
  console.log(`  final initialized: ${summary.final_status?.initialized}`);
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    console.log(HELP);
    return;
  }
  try {
    const summary = await runSmoke(options);
    printSummary(summary, options.json);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    if (options.json) {
      console.log(
        JSON.stringify(
          {
            ok: false,
            frontend_url: options.frontendUrl,
            dashboard_url: dashboardUrl(options.frontendUrl),
            backend_url: options.backendUrl,
            error: message
          },
          null,
          2
        )
      );
      process.exitCode = 1;
      return;
    }
    console.error(`Browser acceptance smoke failed: ${message}`);
    process.exitCode = 1;
  }
}

main();
