import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json({ error: 'Missing submission ID' }, { status: 400 });
    }

    const projectRoot = path.resolve(process.cwd(), '..');
    const pdfPath = path.join(projectRoot, `Final_Filled_${id}.pdf`);

    try {
      // Check if file exists
      await fs.access(pdfPath);
    } catch {
      return NextResponse.json({ error: 'PDF not found' }, { status: 404 });
    }

    const fileContent = await fs.readFile(pdfPath);

    return new NextResponse(fileContent, {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename="Final_Filled_${id}.pdf"`,
      },
    });
  } catch (error) {
    console.error("API error downloading PDF:", error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
