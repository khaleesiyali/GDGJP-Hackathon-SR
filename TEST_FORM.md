# Quick Start - Form Feature Testing

## What's New

✅ Form page with dynamic question flow
✅ Text-to-speech question reading in Japanese
✅ Beautiful yellow question card UI
✅ Answer collection and storage
✅ Success page with PDF download
✅ Complete form-to-PDF workflow

## Start in 30 Seconds

### Terminal 1: Backend

```bash
cd /Users/y4l1/Documents/GDGJP-Hackathon
python -m uvicorn server:app --reload
```

Expected output:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2: Frontend

```bash
cd /Users/y4l1/Documents/GDGJP-Hackathon/ai-privacy-amanuensis
npm run dev
```

Expected output:

```
  ▲ Next.js 16.1.6
  - Local:        http://localhost:3001
```

### Open Browser

```
http://localhost:3001/form
```

## What You'll See

### Step 1: Form Loads

- Yellow card appears with form name
- Text-to-speech reads: "心身障碍者福祉手当認定申請書の申請書があります..."
- Progress shows "1 / 4"

### Step 2: First Question

- Large question text in yellow card
- Waveform bars animate below
- "聞き取り中..." status shows
- Either:
  - 🎤 Click mic button to "listen" (toggles to red)
  - Type answer in text field

### Step 3: Answer & Continue

- Type your answer (or just press Enter)
- Click [送信] button
- System responds: "かしこまりました。ありがとうございます。"
- Next question appears

### Step 4: Repeat

- System asks questions 2/4, 3/4, 4/4
- Progress counter updates
- Same answer flow each time

### Step 5: Success!

- Redirects to success page
- Shows: "申請完了!"
- Submission ID displayed
- [PDFをダウンロード] button ready

### Step 6: Download

- Click [PDFをダウンロード]
- PDF file downloads with your answers
- Can download again or navigate away

## Keyboard Shortcuts

| Action        | Key                        |
| ------------- | -------------------------- |
| Submit Answer | Enter ↩️                   |
| Skip Question | Click [スキップ]           |
| Go Back       | Click [◀]                  |
| Start Over    | Click [別のフォームを入力] |
| Home          | Click [ホームに戻る]       |

## Demo Data (Fallback)

If JSON file not found, form uses 4 default questions:

1. お名前をご記入ください (Name)
2. 生年月日を入力してください (Birth Date)
3. ご自身の障害の種類をお知らせください (Disability Type)
4. ご連絡先のご住所をお知らせください (Address)

## Troubleshooting

### No questions appear?

- Check browser console (F12)
- Verify `/api/form-schema` works:
  ```bash
  curl http://localhost:3001/api/form-schema
  ```

### Text-to-speech not working?

- Check browser speaker/volume
- Try different question
- Works best in Chrome/Safari

### PDF download fails?

- Ensure backend running on port 8000
- Check Network tab in DevTools
- Verify `/api/generate-pdf` called

### Questions skip/don't display?

- Check formData in React DevTools
- Verify formSchema loaded in State
- Check progressStep value

## Test Scenarios

### ✅ Basic Flow

1. Open /form
2. Answer questions with simple text
3. Complete form
4. Download PDF
5. Verify PDF has your answers

### ✅ Skip Questions

1. Open /form
2. Skip some questions [スキップ]
3. Only answer a few
4. Complete form
5. Verify only answered questions in PDF

### ✅ Navigation

1. Open /form
2. Click [◀] to go back
3. Return to home
4. Navigate to /form again
5. Should start fresh form

### ✅ Multiple Downloads

1. Complete form
2. Click [PDFをダウンロード]
3. Download completes
4. Click again
5. Second download works

## Files Modified

| File             | Change                             |
| ---------------- | ---------------------------------- |
| FormPage.tsx     | Complete redesign with yellow card |
| success/page.tsx | PDF download implementation        |
| api/form-schema  | Load form questions                |
| api/generate-pdf | Generate filled PDF                |
| server.py        | PDF generation endpoint            |

## What's Working

✅ Form schema loading
✅ Question display
✅ Text-to-speech (ja-JP)
✅ Answer capture
✅ Progress tracking
✅ Form completion detection
✅ Success page
✅ PDF generation
✅ PDF download

## Optional Features (Next Phase)

- [ ] Voice input recognition (speech-to-text)
- [ ] Connect to Vision.py agent
- [ ] Digital signature capture
- [ ] Email submission
- [ ] Multiple form templates
- [ ] Offline support

---

**Ready to test?** → Open http://localhost:3001/form

**Questions?** → Check FORM_COMPLETE.md for detailed documentation
