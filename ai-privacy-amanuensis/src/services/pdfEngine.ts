import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import QRCode from 'qrcode';

export interface FormData {
  [key: string]: string;
}

/**
 * Generates a PDF document purely client-side ensuring no data leaves the browser.
 */
export async function generatePrivacyPreservingPDF(formData: FormData, title: string = 'Government Form'): Promise<Uint8Array> {
  // Create a new PDF document
  const pdfDoc = await PDFDocument.create();
  
  // Add a blank page
  const page = pdfDoc.addPage();
  const { width, height } = page.getSize();
  
  // Embed standard fonts
  const helveticaFont = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const helveticaBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  
  // Draw the Title
  page.drawText(title, {
    x: 50,
    y: height - 50,
    size: 24,
    font: helveticaBold,
    color: rgb(0, 0, 0),
  });

  // Draw Form Data
  let yPosition = height - 100;
  for (const [key, value] of Object.entries(formData)) {
    page.drawText(`${key}: ${value}`, {
      x: 50,
      y: yPosition,
      size: 14,
      font: helveticaFont,
      color: rgb(0, 0, 0),
    });
    yPosition -= 30;
  }
  
  // Generate a QR Code with a summary (client-side only)
  try {
    const summary = JSON.stringify(formData);
    const qrDataUrl = await QRCode.toDataURL(summary);
    
    // The data URL is in format "data:image/png;base64,..."
    const qrImageBytes = Uint8Array.from(atob(qrDataUrl.split(',')[1]), c => c.charCodeAt(0));
    
    const qrImage = await pdfDoc.embedPng(qrImageBytes);
    const qrDims = qrImage.scale(0.5);
    
    page.drawImage(qrImage, {
      x: width - qrDims.width - 50,
      y: height - qrDims.height - 50,
      width: qrDims.width,
      height: qrDims.height,
    });
  } catch (error) {
    console.warn("Failed to generate QR code for PDF", error);
  }

  // Serialize the PDFDocument to bytes
  const pdfBytes = await pdfDoc.save();
  return pdfBytes;
}

/**
 * Utility to trigger a file download from pdf bytes (client-side)
 */
export function downloadPDF(pdfBytes: Uint8Array, filename: string = 'form.pdf') {
  const blob = new Blob([pdfBytes], { type: 'application/pdf' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
