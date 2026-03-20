import { NextRequest, NextResponse } from 'next/server';
import * as fs from 'fs';
import * as path from 'path';

export async function GET(request: NextRequest) {
  try {
    // The JSON file is in the repository root, not the frontend folder
    const repositoryRoot = path.join(process.cwd(), '..', '..');
    const schemaPath = path.join(repositoryRoot, '心身障碍者福祉手当認定申請書.json');
    
    let schemaBuffer;
    if (fs.existsSync(schemaPath)) {
      schemaBuffer = fs.readFileSync(schemaPath);
      const schema = JSON.parse(schemaBuffer.toString());
      return NextResponse.json(schema);
    }
    
    // If file not found, return fallback schema
    const fallbackSchema = {
      name: '心身障碍者福祉手当認定申請書',
      parameters: {
        properties: {
          applicant_name: {
            description: 'お名前をご記入ください',
            type: 'string'
          },
          birth_date: {
            description: '生年月日を入力してください（例：1990年1月1日）',
            type: 'string'
          },
          disability_type: {
            description: 'ご自身の障害の種類をお知らせください',
            type: 'string'
          },
          contact_address: {
            description: 'ご連絡先のご住所をお知らせください',
            type: 'string'
          }
        }
      }
    };
    
    return NextResponse.json(fallbackSchema);
  } catch (error) {
    console.error('Error loading form schema:', error);
    
    // Return a fallback schema for development
    const fallbackSchema = {
      name: '心身障碍者福祉手当認定申請書',
      parameters: {
        properties: {
          applicant_name: {
            description: 'お名前をご記入ください',
            type: 'string'
          },
          birth_date: {
            description: '生年月日を入力してください（例：1990年1月1日）',
            type: 'string'
          },
          disability_type: {
            description: 'ご自身の障害の種類をお知らせください',
            type: 'string'
          },
          contact_address: {
            description: 'ご連絡先のご住所をお知らせください',
            type: 'string'
          }
        }
      }
    };
    
    return NextResponse.json(fallbackSchema);
  }
}
