import { describe, expect, it } from "vitest";

import {
  COUNTRY_OVERLAYS,
  countryOverlayEntityIds
} from "../src/3d/cesium/countryOverlays";

describe("country overlays", () => {
  it("keeps deterministic country labels and border entities for the globe", () => {
    expect(COUNTRY_OVERLAYS.map((country) => country.name)).toEqual([
      "中国",
      "美国",
      "俄罗斯",
      "印度",
      "巴西",
      "澳大利亚",
      "加拿大",
      "墨西哥",
      "南非",
      "埃及",
      "沙特",
      "德国",
      "法国",
      "英国",
      "日本",
      "印尼"
    ]);

    const ids = countryOverlayEntityIds();
    expect(ids).toHaveLength(COUNTRY_OVERLAYS.length * 2);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("uses closed coarse borders so country outlines render as complete loops", () => {
    for (const country of COUNTRY_OVERLAYS) {
      const border = country.borderDegrees;
      expect(border.length).toBeGreaterThanOrEqual(10);
      expect(border[0]).toBe(border[border.length - 2]);
      expect(border[1]).toBe(border[border.length - 1]);
    }
  });
});
