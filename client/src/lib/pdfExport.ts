import jsPDF from "jspdf";
import html2canvas from "html2canvas";

/**
 * Build a safe, descriptive filename for the comparison PDF.
 * Strips characters not allowed in common filesystems and trims length.
 *
 * Examples:
 *   buildComparisonFilename("Health Story", "Cost Fact")
 *     → "nidm-comparison-health-story-vs-cost-fact-2026-04-30.pdf"
 */
export function buildComparisonFilename(
  labelA: string,
  labelB: string,
  date: Date = new Date()
): string {
  const slug = (s: string) =>
    (s || "narrative")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 32) || "narrative";

  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");

  return `nidm-comparison-${slug(labelA)}-vs-${slug(labelB)}-${yyyy}-${mm}-${dd}.pdf`;
}

interface ExportOptions {
  filename: string;
  /** Optional title rendered as PDF metadata. */
  title?: string;
  /** Optional subject/author for PDF metadata. */
  subject?: string;
  /** Background fill behind the captured DOM (matches dashboard navy by default). */
  background?: string;
}

/**
 * Capture a DOM element and stream it into a multi-page A4 PDF.
 * Long content is sliced vertically across pages so nothing is clipped.
 */
export async function exportElementToPdf(
  element: HTMLElement,
  options: ExportOptions
): Promise<void> {
  const {
    filename,
    title = "NIDM Narrative Comparison",
    subject = "Side-by-side narrative comparison",
    background = "#0E1A33",
  } = options;

  // Render the element to a high-DPI canvas
  const canvas = await html2canvas(element, {
    backgroundColor: background,
    scale: 2,
    useCORS: true,
    logging: false,
    windowWidth: element.scrollWidth,
    windowHeight: element.scrollHeight,
  });

  // A4 portrait in millimetres
  const pdf = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
  pdf.setProperties({
    title,
    subject,
    creator: "NIDM Rwanda Dashboard",
    author: "NIDM Rwanda Dashboard",
  });

  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 8; // mm
  const usableWidth = pageWidth - margin * 2;
  const usableHeight = pageHeight - margin * 2;

  // Convert canvas pixel height into mm at the chosen render width
  const ratio = canvas.height / canvas.width;
  const renderedHeightMm = usableWidth * ratio;

  if (renderedHeightMm <= usableHeight) {
    // Single page fits comfortably
    const imgData = canvas.toDataURL("image/png");
    pdf.addImage(imgData, "PNG", margin, margin, usableWidth, renderedHeightMm);
  } else {
    // Slice the canvas into page-sized chunks vertically
    const pxPerMm = canvas.width / usableWidth;
    const pageSliceHeightPx = Math.floor(usableHeight * pxPerMm);

    let renderedPx = 0;
    let pageIndex = 0;

    while (renderedPx < canvas.height) {
      const sliceHeightPx = Math.min(
        pageSliceHeightPx,
        canvas.height - renderedPx
      );

      const sliceCanvas = document.createElement("canvas");
      sliceCanvas.width = canvas.width;
      sliceCanvas.height = sliceHeightPx;
      const ctx = sliceCanvas.getContext("2d");
      if (!ctx) throw new Error("Failed to acquire 2D context for PDF slice");

      ctx.fillStyle = background;
      ctx.fillRect(0, 0, sliceCanvas.width, sliceCanvas.height);
      ctx.drawImage(
        canvas,
        0,
        renderedPx,
        canvas.width,
        sliceHeightPx,
        0,
        0,
        canvas.width,
        sliceHeightPx
      );

      const sliceImg = sliceCanvas.toDataURL("image/png");
      const sliceMmHeight = sliceHeightPx / pxPerMm;

      if (pageIndex > 0) pdf.addPage();
      pdf.addImage(sliceImg, "PNG", margin, margin, usableWidth, sliceMmHeight);

      renderedPx += sliceHeightPx;
      pageIndex += 1;
    }
  }

  pdf.save(filename);
}
