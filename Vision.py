import json
import logging
from dotenv import load_dotenv
logger = logging.getLogger("form-agent")
logger.setLevel(logging.INFO)
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents import AgentSession, Agent, function_tool
from livekit.plugins import openai, google, silero

load_dotenv(".env.local")
import os
print(f"DEBUG: GOOGLE_API_KEY is {'SET' if os.getenv('GOOGLE_API_KEY') else 'MISSING'}")

import json
import os
import logging
from livekit.agents import Agent, function_tool

logger = logging.getLogger("form-agent")

# 1. 模拟从数据库/文件中读取 JSON 表单
def load_form_from_db(file_path="mock_form.json"):
    # 为了方便你直接测试，如果文件不存在，直接返回一个包含 null 和 已填数据的 Mock 字典
    if not os.path.exists(file_path):
        return {
            "form_id": "doc_8848",
            "form_name": "障害者手帳交付申請書",
            "fields": {
                "氏名（漢字）": None,          # 这个是 null，AI 会去问
                "生年月日": None,             # 这个是 null，AI 会去问
                "国籍": "日本",               # 这个已经有值了，AI 应该忽略它
                "障害の種別": None,           # 这个是 null，AI 会去问
                "連絡先電話番号": None         # 动态新增的 null，AI 也会去问
            }
        }
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 2. 动态生成的 Agent 类
class FormAgent(Agent):
    def __init__(self, form_data: dict):
        self.form_data = form_data
        
        # 核心逻辑：找出所有 value 为 None (null) 的字段名
        missing_fields = []
        for key, value in self.form_data.get("fields", {}).items():
            if value is None:
                missing_fields.append(key)
        
        # 将找出的字段变成字符串，喂给系统提示词
        missing_fields_str = "\n".join([f"- {field}" for field in missing_fields])
        
        instructions = f"""
あなたは日本区役所の親切な職員で、視覚障害のある方の申請書記入を丁寧にサポートします。

現在処理中のフォーム: {self.form_data.get('form_name')}

以下の項目が未入力(null)です。ユーザーに一つずつ質問して、情報を収集してください：
{missing_fields_str}

ルール:
1. 各質問は必ず一つずつ行ってください。一度に複数の項目を聞かないでください。
2. 氏名を聞いた後は、必ず漢字表記を確認してください。
3. 全ての情報を集めたら、最後にまとめて復唱してください。
4. ユーザーが「はい」と明確に同意した後のみ、`submit_form_data` を呼び出してください。
"""
        super().__init__(instructions=instructions)

    # 3. 改为接收通用 JSON 字符串的 Tool
    @function_tool(description="すべての未入力項目が収集できたら、この関数を呼び出してデータを送信します。")
    async def submit_form_data(
        self,
        updated_json_string: str
    ) -> str:
        """
        Args:
            updated_json_string: 収集した情報をすべて埋めた、完全なJSON形式の文字列。
        """
        try:
            # 将 LLM 传回来的字符串解析回 Python 字典
            filled_data = json.loads(updated_json_string)
            
            # 把收集到的数据合并回原始表单中
            for key, value in filled_data.items():
                if key in self.form_data["fields"]:
                    self.form_data["fields"][key] = value

            logger.info(f"\n========================================\n✅ 成功获取完整表单数据并写入:\n{json.dumps(self.form_data, ensure_ascii=False, indent=2)}\n========================================")
            
            # 这里你可以添加将 self.form_data 保存回数据库的逻辑
            
            return "かしこまりました。ただいま書類を作成しております。"
        except json.JSONDecodeError:
            logger.error("LLM 传回来的不是标准 JSON 格式")
            return "すみません、システムエラーが発生しました。もう一度確認させてください。"

# 3. 极简的 Agent 入口
async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # 启动前，先从数据库/本地文件拉取这张表单
    current_form = load_form_from_db()
    
    session = AgentSession(
        stt=openai.STT(language="ja"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="alloy"),
        vad=silero.VAD.load(),
    )

    # 把动态表单传进去
    await session.start(
        room=ctx.room,
        agent=FormAgent(form_data=current_form)
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))