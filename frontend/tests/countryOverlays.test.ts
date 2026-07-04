import { describe, expect, it } from "vitest";

import {
  COUNTRY_OVERLAYS,
  NATURAL_EARTH_COUNTRY_SOURCE_URI,
  NaturalEarthCountryFeatureCollection,
  countryOverlayEntityIds,
  naturalEarthCountryOverlayDefinitions
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

describe("Natural Earth country overlays", () => {
  it("uses a bundled public-domain country boundary source", () => {
    expect(NATURAL_EARTH_COUNTRY_SOURCE_URI).toBe(
      "/assets/natural-earth/ne_110m_admin_0_countries.geojson"
    );
  });

  it("derives deterministic country overlays from GeoJSON features", () => {
    const definitions = naturalEarthCountryOverlayDefinitions(naturalEarthFixture);

    expect(definitions.map((country) => country.id)).toEqual(["aaa", "bbb"]);
    expect(definitions.map((country) => country.name)).toEqual(["Alpha", "Beta"]);
    expect(definitions[0].label).toEqual([10, 20]);
    expect(definitions[0].borderDegrees).toEqual([0, 0, 2, 0, 2, 1, 0, 0]);
    expect(definitions[1].borderDegrees).toEqual([30, 0, 34, 0, 34, 4, 30, 0]);

    const ids = countryOverlayEntityIds(definitions);
    expect(ids).toHaveLength(4);
    expect(new Set(ids).size).toBe(ids.length);
  });
});

const naturalEarthFixture = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        ADM0_A3: "BBB",
        NAME_EN: "Beta",
        LABEL_X: 30,
        LABEL_Y: 2
      },
      geometry: {
        type: "MultiPolygon",
        coordinates: [
          [
            [
              [40, 0],
              [41, 0],
              [41, 1],
              [40, 0]
            ]
          ],
          [
            [
              [30, 0],
              [34, 0],
              [34, 4],
              [30, 0]
            ]
          ]
        ]
      }
    },
    {
      type: "Feature",
      properties: {
        ADM0_A3: "AAA",
        NAME_EN: "Alpha",
        LABEL_X: 10,
        LABEL_Y: 20
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [0, 0],
            [2, 0],
            [2, 1]
          ]
        ]
      }
    }
  ]
} as const satisfies NaturalEarthCountryFeatureCollection;
