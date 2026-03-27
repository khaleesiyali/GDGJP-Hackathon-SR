import json
import logging
import os
import uuid 
import asyncio
import urllib.parse
from dotenv import load_dotenv

from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents import AgentSession, Agent, function_tool
import livekit.rtc
from livekit.plugins import openai, silero

import json
import logging
import os
import uuid 
import asyncio
import urllib.parse
from dotenv import load_dotenv

from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents import AgentSession, Agent, function_tool
from livekit.plugins import openai, silero
import json
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
import os



# Japanese FONT (we used NotoSans, which is a open-sourced font created by google)
font_path = os.path.join("Font", "NotoSansJP-Medium.ttf")
try:
    pdfmetrics.registerFont(TTFont('NotoSans', font_path))
    print("✅ Noto Sans Loading completed")
except Exception as e:
    print(f"❌ Loading failed: {e}")

def convert_to_jp_era(year, month, day):
    """Changing YMD into Japanese era"""
    y, m, d = int(year), int(month), int(day)
    if y >= 2019: 
        return "R", str(y - 2018)  # Reiwa
    elif y >= 1989:
        return "H", str(y - 1988)  # Heisei
    else:
        return "S", str(y - 1925)  # Showa

def fill_pdf_data(user_answers_path, mapping_json_path, transparent_pdf_path="transparent_text.pdf"):
    # 1. Read the dictionary
    with open(user_answers_path, 'r', encoding='utf-8') as f:
        answers = json.load(f)["answers"]
    
    with open(mapping_json_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)["mapping"]
        
    # 2. Generate a empty canvas (For transparent_text.pdf)
    c = canvas.Canvas(transparent_pdf_path)
    c.setFont('NotoSans', 10) 
    
    # 3. (use answer and mapping json to fill the empty canvas)
    smart_fill_pdf(answers, mapping, c)
    
    # 4. Save as transparent_pdf
    c.save()
    print(f"✅ transparent Layer: {transparent_pdf_path}")


def smart_fill_pdf(answers, mapping, c):
    def process_node(ans_node, map_node):
        for key, value in ans_node.items():
            if key not in map_node:
                continue
                
            rule = map_node[key]
            
            if isinstance(value, dict):
                process_node(value, rule)
                continue
                
            # 1. General text (type=text)
            if isinstance(rule, dict) and rule.get("type") == "text" and value:
                c.drawString(rule["x"], rule["y"], str(value))
            elif rule.get("type") == "date_split" and value:
                year, month, day = value.split("-")
                if "year" in rule:
                    c.drawString(rule["year"]["x"], rule["year"]["y"], year)
                if "month" in rule:
                    c.drawString(rule["month"]["x"], rule["month"]["y"], month)
                if "day" in rule:
                    c.drawString(rule["day"]["x"], rule["day"]["y"], day)
            # 2. Spilting the date into YYYY MM DD (type = date_split)
            elif rule.get("type") == "date_split_era" and value:
                # In case the year month day is not complete
                try:
                    year, month, day = value.split("-")
                    era_code, jp_year = convert_to_jp_era(year, month, day)
                    
                    # 1. year
                    if "year" in rule:
                        c.drawString(rule["year"]["x"], rule["year"]["y"], jp_year)
                    # 2. Month
                    if "month" in rule:
                        c.drawString(rule["month"]["x"], rule["month"]["y"], month)
                    # 3. Day
                    if "day" in rule:
                        c.drawString(rule["day"]["x"], rule["day"]["y"], day)
                        
                    # 4. Era
                    if "era" in rule and "options" in rule["era"] and era_code in rule["era"]["options"]:
                        cx = rule["era"]["options"][era_code]["x"]
                        cy = rule["era"]["options"][era_code]["y"]
                        c.circle(cx, cy, 10, stroke=1, fill=0)
                except Exception as e:
                    print(f"⚠️ 日期解析出错: {value}, 错误信息: {e}")

            # 3. For space that need separate character (type = char_spilt)
            elif rule.get("type") == "char_split" and value:
                str_value = str(value) 
                start_x = rule["start_x"]
                spacing_x = rule["spacing_x"]
                y = rule["y"]
                
                # Draw each character into the boxes
                for i, char in enumerate(str_value):
                    current_x = start_x + (i * spacing_x)
                    c.drawString(current_x, y, char)
                    print(f"📍 Draw: {char} at (x:{current_x}, y:{y})")

            # 4. Circle and Check (type = boolean_circle)
            elif rule.get("type") == "boolean_circle" and value or rule.get("type")=="boolean_check" and value:
                if value in rule.get("options", {}):
                    cx = rule["options"][value]["x"]
                    cy = rule["options"][value]["y"]
                    c.circle(cx, cy, 10, stroke=1, fill=0)

            # 5. irregular character spilt (type = irregular)
            elif rule.get("type") == "char_split_irregular" and value:
                str_value = str(value)
                x_coords = rule.get("x_coords", [])
                y = rule["y"]
                
                # put each characters into boxes
                for i, char in enumerate(str_value):
                    if i < len(x_coords): 
                        current_x = x_coords[i]
                        c.drawString(current_x, y, char)
                        print(f"📍 Draw irregular: {char} at (x:{current_x}, y:{y})")
                    else:
                        print(f"⚠️ length exceeded, drop: {char}")
    process_node(answers, mapping)

def merge_pdfs(blank_form_path, text_layer_path, final_output_path):
    """Generating New PDF"""
    # Read empty form
    original_pdf = PdfReader(blank_form_path)
    text_pdf = PdfReader(text_layer_path)
    
    writer = PdfWriter()
    
    # Put transparent text on empty form
    original_page = original_pdf.pages[0]
    text_page = text_pdf.pages[0]
    original_page.merge_page(text_page)
    
    writer.add_page(original_page)
    
    # Generate new User PDF
    with open(final_output_path, "wb") as f:
        writer.write(f)
    print(f"🎉 The new pdf is: {final_output_path}")



logger = logging.getLogger("form-agent")
logger.setLevel(logging.INFO)
load_dotenv(".env.local")

print(f"DEBUG: OPENAI_API_KEY is {'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING'}")

# 1. Extract JSON schema
FORM_DB = {
    "心身障碍者福祉手当認定申請書": "心身障碍者福祉手当認定申請書.json",   # This is our database, although we only have 1 for now
}

def load_form_from_db(form_id: str):
    """Read according JSON file based on the command received from User"""
    file_path = FORM_DB.get(form_id)
    if not file_path or not os.path.exists(file_path):
        logger.error(f"Cant find form id: {form_id}")
        return None
        
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    


# 2. Agent (Form filling and Form retrieving)
class FormAgent(Agent):
    def __init__(self, room):
        # Asking user's purpose
        instructions = """
        あなたは日本の区役所の親切な総合案内の職員です。視覚障害のある方を音声でサポートします。

        【初期対応】
        まずは「こんにちは。Aman AIです。本日はどのようなお手続きでしょうか？『手当の申請をしたい』や『過去の履歴を見たい』など、ご自由にお話しください。

        【会話のルール】
        1. ユーザーに対して、自然で温かいトーンで話しかけてください。
        2. **絶対に忘れないでください**: 新しい質問をする前には、**必ず `update_ui_card` ツールを呼び出して**、画面の表示を現在聞こうとしている質問内容に更新してください。
        3. ツールからシステムメッセージが返ってきたら、自然に会話を続けてください。
        4. ⭐️【音声署名の要求】ユーザーが復唱内容に同意したら、最後に必ず「ありがとうございます。最後に電子署名として、ご本人確認の録音を行います。『この内容で申請します』と声に出して宣言してください。」とお願いしてください。
        【絶対厳守の会話・業務ルール】
        1. 【質問のペース】絶対に箇条書き（1. 2. 3...）で大量の質問を列挙しないでください！視覚障害のある方が覚えやすいよう、**一度の会話で聞くのは「関連する1〜2項目」まで**に制限してください。
        2. 🛑【絶対停止：氏名の漢字分解ルビ確認（最高優先度）】ユーザーの氏名を聞き取った直後は、他の質問を一旦停止してください。聞き取った名前の漢字を**一文字ずつ、その漢字を含む「誰もが知っている一般的な単語」を使って**説明し、ユーザーに確認を求めてください。
            ⚠️【警告：特定の単語の使い回し禁止】入力された名前に合わせて、その都度適切な単語を動的に生成してください。
            発言フォーマット：「[氏名]様ですね。漢字の確認ですが、1文字目は[その漢字を使った一般的な単語]の[漢字]、2文字目は[別の一般的な単語]の[漢字]...で合っていますか？」
            **英語モードの場合**：英語のスペルを**アルファベット1文字ずつ、簡単な英単語（フォネティックコード）を使って**スペルアウトして確認してください（例：「A as in Apple, L as in Lion, I as in Ice... Is that correct?」）。
            ※ユーザーが「はい」と答えるまで、絶対に住所や電話番号の質問に進んではいけません。
        3. 【優しくフォロー】不足している項目だけを追加で質問してください。
        4. 【論理的チェック】ユーザーの回答が質問の意図と明らかに合っていない場合、音声認識エラーと判断し、優しく聞き直してください。
        5. 【最終確認】全ての必要な情報を集め終わったら、内容をまとめて復唱してください。
        6. ⭐️【音声署名の要求】ユーザーが復唱内容に同意したら、最後に必ず「ありがとうございます。最後に電子署名として、ご本人確認の録音を行います。『この内容で申請します』と声に出して宣言してください。」とお願いしてください。
        7. 【途中終了の対応】ユーザーが記入の終了を明言した場合は、残りの未記入項目の質問をスキップし、直ちに【最終確認】と【音声署名の要求】に進んでください。
        8. 【送信条件】ユーザーが上記の宣言を声に出して言ったのを確認した後のみ、`submit_form_data` を呼び出してください。
        9. ⚠️【厳密なデータフォーマット】`submit_form_data` に渡すJSON構造は完全に維持してください。収集できなかった項目は `null` または `""` にしてください。
        10. 【徹底質問】ユーザーが「途中終了」を宣言しない限り、全項目が埋まるまで質問を続けてください、途中終了にしても最後に電子署名が必要です。
        11. 【言語モードの厳格な切り替えとデータ分離】
            - ⚠️**音声による切り替えの絶対ルール**: ユーザーが音声で「英語で話して」等と要求した場合、**絶対にその場ですぐに言語を切り替えないでください**。まずは必ず「英語に切り替えますか？ Would you like to switch to English?」とバイリンガルで質問し、同意を待ってください。
            - **同意後のモード固定**: ユーザーが同意した後、初めてモードを完全に切り替えます。以降は言語を混ぜることは厳禁です。
            - **データ保存の絶対ルール**: 会話が英語モードであっても、JSONに保存するデータは絶対に日本語に翻訳して記録してください。
        12.🚫【システム用語・関数名の発言禁止（超重要）】ユーザーとの会話中に、`update_ui_card`、`submit_form_data`、`JSON`、`関数`、`ツール`、`システム` などの内部プログラム用語や英語の関数名を絶対に口に出さないでください。「画面の表示を更新します」「申請の送信処理を行います」のように、人間のアシスタントとして極めて自然な言葉に置き換えて話してください。
        """
        super().__init__(instructions=instructions)
        self.room = room
        self.base_instructions = instructions
        self.current_form_data = None
        self.expected_format = ""
        self.last_submission = None

    # ----------------------------------------------------
    # Form filling Mode
    # ----------------------------------------------------
    @function_tool(description="ユーザーが新しい申請書を作成したい場合に呼び出します。ユーザーの会話内容から最適なフォームを推測して選択してください。")
    async def start_form_filling(self, form_type: str) -> str:
        """
        Args:
            form_type: ユーザーの目的に応じて以下のいずれかのIDを指定してください：
            - "心身障碍者福祉手当認定申請書" : 「福祉手当」「障害者手当」「お金の申請」「申請書」などのキーワードが出た場合。
        """
        logger.info(f"🧠 AI 传进来的原始表单类型: {form_type}")
        if form_type not in ["心身障碍者福祉手当認定申請書"]:
            logger.warning(f"⚠️ 捕捉到 AI 幻觉！瞎编了 [{form_type}]，已强制纠正为 [心身障碍者福祉手当認定申請書]！")
            form_type = "心身障碍者福祉手当認定申請書"

        self.current_form_data = load_form_from_db(form_type)
        
        if not self.current_form_data:
            return "システムエラー：該当するフォームが見つかりませんでした。ユーザーに「現在その申請書には対応していません」と謝罪し、他の要件がないか聞いてください。"

        # Trigger Frontend Navigation
        if self.room:
            payload = json.dumps({"action": "navigate", "destination": "/form"}).encode('utf-8')
            asyncio.create_task(self.room.local_participant.publish_data(payload, reliable=True))

        properties = self.current_form_data.get("parameters", {}).get("properties", {})
        
    
        self.expected_format = json.dumps(properties, ensure_ascii=False, indent=2)
        missing_fields = []
        for key, value in properties.items():
            desc = value.get("description", "")
            missing_fields.append(f"{key} ({desc})" if desc else key)
            
        missing_fields_str = "\n".join([f"- {field}" for field in missing_fields])
        form_name = self.current_form_data.get("name", "未命名申請フォーム")

        logger.info(f"Successfully loading [{form_name}]，ready for action")

        # Core rules
        return f"""【システム指示：ここからモードを切り替えてください】
        フォーム「{form_name}」がロードされました。ここからは「申請書記入サポート係」として振る舞い。
        
        ⚠️【最優先アクション：フォームの確認】⚠️
        まずはユーザーに「{form_name}ですね。こちらの作成を始めてもよろしいでしょうか？」とだけ聞いて、ユーザーの同意（「はい」「お願いします」など）を待ってください。同意を得る前に、個人情報の質問を始めてはいけません！
        
        以下の項目をユーザーに質問してください：
        {missing_fields_str}

        【必須の出力JSON構造テンプレート】:
        {self.expected_format}
        """
# ----------------------------------------------------
    # Form retrieving Mode
# ----------------------------------------------------   

    @function_tool(description="新しい質問をする直前に【必ず・毎回】呼び出します。画面のUIカードを更新します。titleは質問の短い見出し、descriptionは画面に表示する詳しい説明文を指定します。（※現在ユーザーと話している言語に合わせて、titleとdescriptionの言語も翻訳して出力してください）")
    async def update_ui_card(self, title: str, description: str) -> str:
        logger.info(f"📡 UIカード動的更新: {title}")
        if self.room:
            payload = json.dumps({
                "action": "update_card", 
                "title": title,
                "description": description
            }).encode('utf-8')
            asyncio.create_task(self.room.local_participant.publish_data(payload, reliable=True))
        return "UI card successfully updated, now you can ask the user the question verbally."

    @function_tool(description="ユーザーがすべての質問に答え終わり、記入内容の確認も完了した後に呼び出します。フロントエンドを自動的に「手続き完了」画面に移動させます。")
    async def finish_form(self) -> str:
        logger.info("📡 完了通知シグナル！")
        if self.room:
            destination = "/success"
            if self.last_submission:
                encoded_data = urllib.parse.quote(json.dumps(self.last_submission))
                sub_id = self.last_submission.get("submission_id", "")
                destination = f"/success?formData={encoded_data}&submissionId={sub_id}"
                
            payload = json.dumps({"action": "navigate", "destination": destination}).encode('utf-8')
            asyncio.create_task(self.room.local_participant.publish_data(payload, reliable=True))
        return "Navigating to success"

    @function_tool(description="ユーザーが過去の申請履歴（マイファイル）を見たいと言った場合に呼び出します。")
    async def open_my_files(self) -> str:
        logger.info("📡 触发信号：通知前端网页跳转到 MyFile 页面！")
        if self.room:
            payload = json.dumps({"action": "navigate", "destination": "/files"}).encode('utf-8')
            asyncio.create_task(self.room.local_participant.publish_data(payload, reliable=True))
        return """
        【システム指示】
        フロントエンドにマイファイルを開くシグナルを送信しました。
        ユーザーに「はい、画面に過去の申請履歴を表示しました。読み上げることも可能ですが、いかがなさいますか？」と伝えてください。
        """


    # 3. Save the data as result_userid.json
    @function_tool(description="⚠️【警告：無断送信禁止】全項目が埋まっても、絶対にすぐ呼び出さないでください！必ず先にユーザーへ「『この内容で申請します』と声に出して宣言してください」とお願いし、ユーザーが実際にその言葉を発声したのを確認した場合【のみ】、この関数を実行してデータを送信してください。")
    async def submit_form_data(self, updated_json_string: str) -> str:
        try:
            user_answers = json.loads(updated_json_string)
            submission_id = str(uuid.uuid4())[:8]
            form_name = self.current_form_data.get("name", "unknown_form") if self.current_form_data else "unknown_form"
            
            final_submission = {
                "form_name": form_name,
                "submission_id": submission_id,
                "status": "completed",
                "answers": user_answers
            }
            self.last_submission = final_submission

            new_file_name = f"result_{submission_id}.json"
            with open(new_file_name, "w", encoding="utf-8") as f:
                json.dump(final_submission, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 成功！新建了独立的文件: {new_file_name}")
            final_pdf_name = f"Final_Filled_{submission_id}.pdf"
            fill_pdf_data(new_file_name, "心身障碍者福祉手当認定申請書Mapping.json", "transparent_text.pdf")
            merge_pdfs("blank_form.pdf", "transparent_text.pdf", final_pdf_name)
            logger.info(f"📄 PDF 生成成功: {final_pdf_name}")

            # Send Navigation Signal to Success Page
            if self.room:
                payload = json.dumps({
                    "action": "navigate", 
                    "destination": f"/success?submission_id={submission_id}"
                }).encode('utf-8')
                asyncio.create_task(self.room.local_participant.publish_data(payload, reliable=True))

            return """
            お疲れ様でした。無事に電子署名の録音と申請データの送信が完了し、正式な申請書類が作成されました。
            作成された書類は、アプリ内の「マイファイル」からいつでもご確認いただけます。
            本日はご利用いただき、本当にありがとうございました。
            """

        except json.JSONDecodeError:
            return "すみません、システムエラーが発生しました。"

# 4. Choose what LLM to use and start the conversation
async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    session = AgentSession(
        stt=openai.STT(), # Removed language="ja" to allow auto-detection for English and Japanese
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="alloy"),
        vad=silero.VAD.load(min_silence_duration=0.5),
    )


async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    

    session = AgentSession(
        stt=openai.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="alloy"),
        vad=silero.VAD.load(min_silence_duration=0.5),
    )

    my_agent = FormAgent(room=ctx.room)

    await session.start(
        room=ctx.room,
        agent=my_agent  #
    )
    logger.info("✅ AI connected")
# The Language system and camera system start right here
# Instead of letting it remember the chat history and repeat based on that (What ctx is doing), I used update instruction.
    @ctx.room.on("data_received")
    def on_data_received(dp: livekit.rtc.DataPacket, **kwargs):
        try:
            payload = json.loads(dp.data.decode("utf-8"))
            
            if payload.get("action") == "camera_scan":
                content = payload.get("content", "")
                logger.info(f"📸 カメラからの書類データを取得しました！\n{content}")
                
                # Three separate task
                async def handle_camera_scan():
                    # 1. Stop all action
                    session.interrupt() 
                    # 2. Injecting new command
                    new_inst = my_agent.base_instructions + f"\n\n【緊急タスク】カメラから以下の情報を読み取りました:\n{content}\nこれをもとに、残りの空欄を埋めるための質問を開始してください。"
                    await my_agent.update_instructions(new_inst)
                    # 3. Speaking
                    session.say("カメラから書類の情報を読み取りました。いくつか確認と、不足している項目について順番に質問させていただきますね。", allow_interruptions=True)
                    
                asyncio.create_task(handle_camera_scan())
                    
            elif payload.get("action") == "set_language":
                lang = payload.get("lang")
                logger.info(f"Language switched to {lang}")
                
                async def force_switch_language():
                    # 1. Stop talking
                    session.interrupt() 
                    
                    if lang == "en":
                        # 2. Injecting
                        # 🌟 加强版英文洗脑包：点名道姓要求翻译 title 和 description
                        new_inst = my_agent.base_instructions + "\n\n【CRITICAL OVERRIDE】ユーザーがUIボタンで英語モードに切り替えました。これ以降の会話は100%完全に英語で行ってください。さらに、ツール機能の仕様に関わらず、**`update_ui_card` ツールを呼び出す際の `title` と `description` の引数も【必ず英語に翻訳して】出力してください**。⚠️【絶対厳守：JSONデータの行政標準日本語化】⚠️ ただし、JSONに保存する「すべての回答データ(Value)」は、ユーザーが英語で発話した内容であっても、**日本の区役所に提出できる正式な日本語フォーマット（適切な漢字・ひらがな・カタカナを用いた表記）**に必ず翻訳・変換して保存してください。（例: 'Tokyo, Nerima Ward' と言われたら必ず '東京都練馬区' に変換し、'Nelima Building' のような建物名はそのままカタカナや英語で正確に記録すること）。アルファベットの直訳や不自然な日本語での保存は厳禁です。"
                        await my_agent.update_instructions(new_inst)
                        # 3. talking
                        session.say("英語に切り替えますか？ Would you like to switch to English?", allow_interruptions=True)
                    else:
                        new_inst = my_agent.base_instructions + "\n\n【CRITICAL OVERRIDE】ユーザーがUIボタンで日本語モードに切り替えました。これ以降は100%完全に日本語のみで会話・UI更新を行ってください。JSON入力も日本語で。"
                        await my_agent.update_instructions(new_inst)
                        session.say("日本語に戻しますか？ Would you like to switch back to Japanese?", allow_interruptions=True)

                # 发射任务
                asyncio.create_task(force_switch_language())

        except Exception as e:
            logger.error(f"Error processing data channel message: {e}")

    greeting_text = "こんにちは、Aman AIです。本日はどのようなお手続きでしょうか？『手当の申請をしたい』や『過去の履歴を見たい』など、ご自由にお話しください。"
    
    try:
        await session.say(greeting_text, allow_interruptions=True)
        logger.info("🗣️ Start Speaking")
    except AttributeError:
        logger.warning("SDK version not compatiable")
        new_inst = my_agent.instructions + "\n\n最初の挨拶をしてください。"
        asyncio.create_task(my_agent.update_instructions(new_inst))

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))