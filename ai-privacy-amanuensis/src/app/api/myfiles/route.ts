import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET() {
  try {
    // The Python backend saves files in the root folder /Users/.../GDGJP-Hackathon/ 
    // Since Next.js is inside ai-privacy-amanuensis/, the root folder is one level up.
    // However, if we run both inside Amanuensis, process.cwd() is ai-privacy-amanuensis.

    const projectRoot = path.resolve(process.cwd(), '..');

    const files = await fs.readdir(projectRoot);
    const jsonFiles = files.filter(f => f.startsWith('result_') && f.endsWith('.json'));

    const submissions = [];

    for (const file of jsonFiles) {
      const filePath = path.join(projectRoot, file);
      try {
        const fileContent = await fs.readFile(filePath, 'utf-8');
        const data = JSON.parse(fileContent);

        // Use file modification time as submission date
        const stats = await fs.stat(filePath);

        submissions.push({
          filename: file,
          form_name: data.form_name || "不明なフォーム",
          submission_id: data.submission_id || file.replace('result_', '').replace('.json', ''),
          timestamp: stats.mtime.toISOString(),
          data: data.answers
        });
      } catch (err) {
        console.error(`Failed to parse ${file}:`, err);
      }
    }

    // Sort by newest first
    submissions.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

    // Inject Working Demo File
    submissions.unshift({
      filename: "demo.pdf",
      form_name: "【デモ版】完了済み心身障碍者福祉手当認定申請書",
      submission_id: "DEMO-9999",
      timestamp: new Date().toISOString(),
      data: { isDemo: true }
    });

    return NextResponse.json({ submissions });
  } catch (error) {
    console.error("API error reading myfiles:", error);
    return NextResponse.json({ error: 'Internal server error', submissions: [] }, { status: 500 });
  }
}
