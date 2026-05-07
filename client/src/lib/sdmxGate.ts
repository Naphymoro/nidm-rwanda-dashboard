import type { ParsedNarrative } from "./narrativeParser";

export type NarrativeInputFormat = "csv" | "narrative" | "sdmx";

export interface SdmxGateReport {
  accepted: boolean;
  exchangeId: string;
  filename: string;
  inputFormat: NarrativeInputFormat;
  outputFormat: "SDMX-NIDM narrative observation set";
  observations: number;
  dimensions: string[];
  measures: string[];
  warnings: string[];
  errors: string[];
}

export interface SdmxNarrativePayload {
  header: {
    id: string;
    prepared: string;
    sender: string;
    name: string;
  };
  structure: {
    dimensions: string[];
    measures: string[];
    attributes: string[];
  };
  dataSets: Array<{
    action: "Replace";
    observations: Array<{
      key: string;
      dimensions: {
        narrative: string;
        type: string;
        target: string;
        source: ParsedNarrative["source"];
      };
      measures: {
        E: number;
        C: number;
        tau: number;
        kappa: number;
        phi: number;
      };
      attributes: {
        label: string;
        quote: string;
        uploadedAt: string;
      };
    }>;
  }>;
}

const DIMENSIONS = ["narrative", "type", "target", "source"];
const MEASURES = ["E", "C", "tau", "kappa", "phi"];

function isUnitInterval(value: number) {
  return Number.isFinite(value) && value >= 0 && value <= 1;
}

export function buildSdmxGateReport(
  narratives: ParsedNarrative[],
  inputFormat: NarrativeInputFormat,
  filename: string
): SdmxGateReport {
  const warnings: string[] = [];
  const errors: string[] = [];

  if (narratives.length === 0) {
    errors.push("No narrative observations were detected.");
  }

  narratives.forEach((narrative, index) => {
    const row = index + 1;
    if (!narrative.key) errors.push(`Row ${row} is missing key.`);
    if (!narrative.label) errors.push(`Row ${row} is missing label.`);
    if (!narrative.quote) warnings.push(`Row ${row} has no quote/body text.`);
    if (!narrative.targets) warnings.push(`Row ${row} has no target audience.`);

    MEASURES.forEach((measure) => {
      const value = narrative[measure as keyof Pick<ParsedNarrative, "E" | "C" | "tau" | "kappa" | "phi">];
      if (!isUnitInterval(value)) {
        errors.push(`Row ${row} has invalid ${measure}; expected a number from 0 to 1.`);
      }
    });
  });

  return {
    accepted: errors.length === 0,
    exchangeId: `NIDM-${Date.now().toString(36).toUpperCase()}`,
    filename,
    inputFormat,
    outputFormat: "SDMX-NIDM narrative observation set",
    observations: narratives.length,
    dimensions: DIMENSIONS,
    measures: MEASURES,
    warnings: Array.from(new Set(warnings)),
    errors: Array.from(new Set(errors)),
  };
}

export function buildSdmxNarrativePayload(
  narratives: ParsedNarrative[],
  filename: string,
  exchangeId = `NIDM-${Date.now().toString(36).toUpperCase()}`
): SdmxNarrativePayload {
  return {
    header: {
      id: exchangeId,
      prepared: new Date().toISOString(),
      sender: "NIDM Rwanda Dashboard",
      name: filename,
    },
    structure: {
      dimensions: DIMENSIONS,
      measures: MEASURES,
      attributes: ["label", "quote", "uploadedAt"],
    },
    dataSets: [
      {
        action: "Replace",
        observations: narratives.map((narrative) => ({
          key: narrative.key,
          dimensions: {
            narrative: narrative.key,
            type: narrative.type,
            target: narrative.targets,
            source: narrative.source,
          },
          measures: {
            E: narrative.E,
            C: narrative.C,
            tau: narrative.tau,
            kappa: narrative.kappa,
            phi: narrative.phi,
          },
          attributes: {
            label: narrative.label,
            quote: narrative.quote,
            uploadedAt: new Date(narrative.uploadedAt).toISOString(),
          },
        })),
      },
    ],
  };
}

export function summarizeSdmxPayload(payload: SdmxNarrativePayload) {
  return {
    id: payload.header.id,
    observations: payload.dataSets[0]?.observations.length ?? 0,
    measures: payload.structure.measures.join(", "),
    dimensions: payload.structure.dimensions.join(", "),
  };
}
