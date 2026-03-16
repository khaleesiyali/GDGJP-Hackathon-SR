import json
import logging
import os
import uuid 
from dotenv import load_dotenv

from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents import AgentSession, Agent, function_tool
from livekit.plugins import openai, silero

# 初始化日志和环境变量
logger = logging.getLogger("form-agent")
logger.setLevel(logging.INFO)
load_dotenv(".env.local")

print(f"DEBUG: OPENAI_API_KEY is {'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING'}")

# 1. 加载你的 Agent JSON Schema
def load_form_from_db(file_path="mock_form.json"):
    if not os.path.exists(file_path):
        logger.error(f"找不到 {file_path}！请确保文件存在。")
        return {}
        
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 2. AGENT 定义
class FormAgent(Agent):
    def __init__(self, form_data: dict):
        self.form_data = form_data
        
        properties = self.form_data.get("parameters", {}).get("properties", {})
        
        missing_fields = []
        for key, value in properties.items():
            description = value.get("description", "")
            if description:
                missing_fields.append(f"{key} ({description})")
            else:
                missing_fields.append(key)
        
        missing_fields_str = "\n".join([f"- {field}" for field in missing_fields])
        form_name = self.form_data.get("name", "未命名申請フォーム")
        
        # ⭐️ 新增：把你的 Agent JSON 结构转换成字符串，准备塞进 Prompt 里吓唬它
        expected_format = json.dumps(properties, ensure_ascii=False, indent=2)
        
        # 优化后的 Prompt (注意看新增的第6点)
        instructions = f"""
あなたは日本の区役所の親切な職員で、視覚障害のある方の申請書記入を丁寧にサポートします。

現在処理中のフォーム: {form_name}

以下の項目について、ユーザーから情報を収集してください：
{missing_fields_str}

会話のルール:
1. 【質問のグループ化】関連する項目はまとめて質問してください。
2. 【優しくフォロー】不足している項目だけを追加で質問してください。
3. 【漢字の確認】氏名を聞き取った後は、必ず漢字表記を確認してください。
4. 【最終確認】全ての必要な情報を集め終わったら、内容をまとめて復唱してください。
5. 【送信条件】ユーザーが明確に同意した後のみ、`submit_form_data` を呼び出してください。
6. ⚠️【超重要：厳密なデータフォーマット】⚠️
`submit_form_data` に渡す `updated_json_string` は、必ず以下のJSON構造(スキーマ)を完全に維持してください!勝手に構造をFlattenしたり、キーの名前を変えたりすることは絶対に禁止です。収集できなかった項目は `null` または `""` にしてください。

【必須の出力JSON構造テンプレート】:
{expected_format}
"""
        super().__init__(instructions=instructions)

    # 3. 接收大模型整理好的最终数据并保存
    @function_tool(description="すべての必要な項目が収集できたら、この関数を呼び出してデータを送信します。")
    async def submit_form_data(
        self,
        updated_json_string: str
    ) -> str:
        """
        Args:
            updated_json_string: 収集した情報をすべて埋めた、完全なJSON形式の文字列。
        """
        try:
            # 解析大模型传回来的“用户回答”
            user_answers = json.loads(updated_json_string)
            
            # ⭐️ 核心修改 2：生成唯一的申请单号，不覆盖原模板
            submission_id = str(uuid.uuid4())[:8]
            
            final_submission = {
                "form_name": self.form_data.get("name", "unknown_form"),
                "submission_id": submission_id,
                "status": "completed",
                "answers": user_answers  # 大模型收集到的所有数据都在这里
            }

            # 存成一个独立的文件
            new_file_name = f"result_{submission_id}.json"
            with open(new_file_name, "w", encoding="utf-8") as f:
                json.dump(final_submission, f, ensure_ascii=False, indent=2)

            logger.info(f"\n========================================\n✅ 成功！新建了独立的文件: {new_file_name}\n========================================")
            
            return "かしこまりました。ただいま書類を作成しております。本日はありがとうございました。"

        except json.JSONDecodeError:
            logger.error("LLM 传回来的不是标准 JSON 格式")
            return "すみません、システムエラーが発生しました。もう一度確認させてください。"

# 4. 启动逻辑
async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    current_form = load_form_from_db()
    
    session = AgentSession(
        stt=openai.STT(language="ja"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="alloy"),
        vad=silero.VAD.load(),
    )
    
    await session.start(
        room=ctx.room,
        agent=FormAgent(form_data=current_form)
    )
    logger.info("✅ AI 已连接！可以在前端/Sandbox发送消息唤醒它了。")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))