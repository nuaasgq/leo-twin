import {
  Cartesian2,
  Cartesian3,
  Color,
  DistanceDisplayCondition,
  Entity,
  EntityCollection,
  LabelStyle,
  PolylineGlowMaterialProperty,
  VerticalOrigin
} from "cesium";

const DEPTH_TEST_DISABLE_DISTANCE = 1_000_000_000_000;
const COUNTRY_LABEL_HEIGHT_M = 18_000;

export interface CountryOverlayDefinition {
  id: string;
  name: string;
  label: readonly [number, number];
  borderDegrees: readonly number[];
}

export const COUNTRY_OVERLAYS: readonly CountryOverlayDefinition[] = [
  {
    id: "china",
    name: "中国",
    label: [104, 35],
    borderDegrees: [73, 18, 86, 49, 124, 53, 135, 42, 123, 21, 100, 20, 73, 18]
  },
  {
    id: "united-states",
    name: "美国",
    label: [-98, 39],
    borderDegrees: [-125, 25, -124, 49, -67, 49, -66, 25, -98, 24, -125, 25]
  },
  {
    id: "russia",
    name: "俄罗斯",
    label: [95, 61],
    borderDegrees: [28, 49, 45, 70, 120, 76, 170, 66, 160, 50, 90, 46, 28, 49]
  },
  {
    id: "india",
    name: "印度",
    label: [78, 22],
    borderDegrees: [68, 8, 77, 35, 90, 27, 88, 20, 80, 7, 68, 8]
  },
  {
    id: "brazil",
    name: "巴西",
    label: [-52, -10],
    borderDegrees: [-74, 5, -50, 5, -34, -8, -44, -33, -64, -31, -74, 5]
  },
  {
    id: "australia",
    name: "澳大利亚",
    label: [134, -25],
    borderDegrees: [113, -11, 154, -11, 153, -39, 115, -36, 113, -11]
  },
  {
    id: "canada",
    name: "加拿大",
    label: [-106, 58],
    borderDegrees: [-141, 49, -132, 70, -95, 74, -53, 60, -66, 45, -141, 49]
  },
  {
    id: "mexico",
    name: "墨西哥",
    label: [-102, 23],
    borderDegrees: [-117, 14, -111, 32, -97, 27, -86, 21, -91, 15, -117, 14]
  },
  {
    id: "south-africa",
    name: "南非",
    label: [24, -29],
    borderDegrees: [16, -35, 33, -35, 32, -22, 26, -22, 16, -35]
  },
  {
    id: "egypt",
    name: "埃及",
    label: [30, 27],
    borderDegrees: [25, 22, 36, 22, 35, 32, 25, 31, 25, 22]
  },
  {
    id: "saudi-arabia",
    name: "沙特",
    label: [45, 24],
    borderDegrees: [35, 16, 55, 16, 56, 31, 40, 32, 35, 16]
  },
  {
    id: "germany",
    name: "德国",
    label: [10, 51],
    borderDegrees: [6, 47, 15, 48, 15, 55, 6, 55, 6, 47]
  },
  {
    id: "france",
    name: "法国",
    label: [2, 46],
    borderDegrees: [-5, 42, 8, 43, 8, 51, -5, 51, -5, 42]
  },
  {
    id: "united-kingdom",
    name: "英国",
    label: [-2, 54],
    borderDegrees: [-8, 50, 2, 51, 1, 59, -7, 58, -8, 50]
  },
  {
    id: "japan",
    name: "日本",
    label: [138, 37],
    borderDegrees: [130, 31, 142, 35, 146, 44, 139, 45, 130, 31]
  },
  {
    id: "indonesia",
    name: "印尼",
    label: [118, -2],
    borderDegrees: [95, -6, 108, 5, 125, 2, 141, -4, 132, -10, 112, -9, 95, -6]
  }
];

export function installCountryOverlays(
  entities: EntityCollection,
  cache: Map<string, Entity>
): void {
  for (const country of COUNTRY_OVERLAYS) {
    upsertCountryLabel(entities, cache, country);
    upsertCountryBorder(entities, cache, country);
  }
}

export function countryOverlayEntityIds(): readonly string[] {
  return COUNTRY_OVERLAYS.flatMap((country) => [
    countryEntityId(country, "label"),
    countryEntityId(country, "border")
  ]);
}

function upsertCountryLabel(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  country: CountryOverlayDefinition
): void {
  const id = countryEntityId(country, "label");
  if (cache.has(id)) {
    return;
  }
  const [longitude, latitude] = country.label;
  const entity = entities.add({
    id,
    name: country.name,
    position: Cartesian3.fromDegrees(longitude, latitude, COUNTRY_LABEL_HEIGHT_M),
    label: {
      text: country.name,
      font: "12px sans-serif",
      fillColor: Color.fromCssColorString("#f1fbff"),
      outlineColor: Color.fromCssColorString("#04131a"),
      outlineWidth: 3,
      style: LabelStyle.FILL_AND_OUTLINE,
      verticalOrigin: VerticalOrigin.CENTER,
      pixelOffset: new Cartesian2(0, 0),
      disableDepthTestDistance: DEPTH_TEST_DISABLE_DISTANCE,
      distanceDisplayCondition: new DistanceDisplayCondition(0, 28_000_000)
    }
  });
  cache.set(id, entity);
}

function upsertCountryBorder(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  country: CountryOverlayDefinition
): void {
  const id = countryEntityId(country, "border");
  if (cache.has(id)) {
    return;
  }
  const entity = entities.add({
    id,
    name: `${country.name} border`,
    polyline: {
      positions: Cartesian3.fromDegreesArray(Array.from(country.borderDegrees)),
      width: 1.1,
      material: new PolylineGlowMaterialProperty({
        color: Color.fromCssColorString("#bff3ff").withAlpha(0.52),
        glowPower: 0.16
      })
    }
  });
  cache.set(id, entity);
}

function countryEntityId(
  country: CountryOverlayDefinition,
  layer: "label" | "border"
): string {
  return `country-${layer}:${country.id}`;
}
