"""
Insurance Sales MCP — Discord Bot MVP

Quick-start a Discord bot that uses our insurance-sales MCP Server as its tool backend.
Run: pip install discord.py httpx python-dotenv
     uv run discord_bot.py
"""

import os, json, asyncio
from pathlib import Path
from typing import Optional
import discord
from discord.ext import commands, slash_commands

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ENV = Path(__file__).parent / ".env"
if ENV.exists():
    from dotenv import load_dotenv
    load_dot_ENV(ENV)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:18060/mcp")
MCP_API_KEY = os.getenv("SERVER_API_KEY", "")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
BOT_NAME = os.getenv("BOT_NAME", "Insurance Advisor Bot")

# ---------------------------------------------------------------------------
# MCP Client (thin HTTP wrapper)
# ---------------------------------------------------------------------------
class MCPClient:
    """Minimal HTTP client for our insurance-sales MCP Server."""
    
    def __init__(self, url: str, api_key: str):
        self.url = url.rstrip("/") + "/tools"
        self.api_key = api_key

    async def call(self, tool_name: str, params: dict) -> dict:
        import httpx
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.url}/{tool_name}",
                json=params,
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def list_tools(self) -> list[dict]:
        """List all available MCP tools."""
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.url}/", headers={"X-API-Key": self.api_key})
            resp.raise_for_status()
            return resp.json().get("tools", [])

# ---------------------------------------------------------------------------
# Bot App
# ---------------------------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix="/",
    intents=intents,
    help_command=None,  # use slash commands only
)

mcp: Optional[MCPClient] = None

@bot.event
async def on_ready():
    await bot.tree.sync()  # sync slash commands
    print(f"✅ {BOT_NAME} online as {bot.user}")

# ---------------------------------------------------------------------------
# Slash Commands (auto-generated from MCP tools)
# ---------------------------------------------------------------------------
DISCLAIMER = (
    "\n\n⚠️ *本建议仅供参考，不构成任何保险购买或投资建议。"
    "最终产品推荐需由持牌代理人根据客户实际情况评估。*\n"
    "*This recommendation is for reference only and does not constitute "
    "any insurance purchase or investment advice.*"
)

def build_slash_command(tool_name: str, description: str):
    """Dynamically create a slash command from an MCP tool schema."""
    
    async def handler(ctx, **kwargs):
        if mcp is None:
            await ctx.respond("❌ MCP Server未连接")
            return
        
        result = await mcp.call(tool_name, kwargs)
        
        # Extract the useful part of the response
        output = result.get("result", result.get("output", json.dumps(result, ensure_ascii=False)))
        
        if isinstance(output, dict):
            output = json.dumps(output, indent=2, ensure_ascii=False)
        elif not isinstance(output, str):
            output = str(output)
        
        await ctx.respond(f"{output}{DISCLAIMER}")
    
    # Create slash command with dynamic options
    cmd = slash_commands.slash_command(
        name=tool_name.replace("_", "-"),
        description=f"MCP tool: {description}" if description else f"Use MCP tool: {tool_name}",
    )(handler)
    return cmd

# Register commands dynamically when bot is ready
@bot.event
async def on_ready():
    await super(InsuranceBot, bot).on_ready()  # type: ignore
    
    global mcp
    mcp = MCPClient(MCP_SERVER_URL, MCP_API_KEY)
    
    try:
        tools = await mcp.list_tools()
        for tool in tools:
            tname = tool.get("name", "")
            tdesc = tool.get("description", "")
            if tname:
                cmd = build_slash_command(tname, tdesc)
                bot.tree.add_command(cmd)
        await bot.tree.sync()
        print(f"✅ 已注册 {len(tools)} 个 slash commands from MCP tools")
    except Exception as e:
        print(f"⚠️ 无法从MCP动态加载commands: {e}")
        # Fallback: register hardcoded commands
        await _register_fallback_commands()

# ---------------------------------------------------------------------------
# Fallback: Hardcoded slash commands (always available)
# ---------------------------------------------------------------------------
@bot.slash_command(name="compliance-check", description="合规检测")
async def cmd_compliance_check(ctx, text: str = discord.SlashOption(description="待检测文案")):
    result = await mcp.call("compliance_check", {"text": text, "strict_mode": True})
    status = "✅ 合规通过" if not result.get("violations") else f"❌ {len(result['violations'])}条违规"
    await ctx.respond(f"{status}\n\n{result.get('summary', '')}{DISCLAIMER}")

@bot.slash_command(name="needs-assessment", description="客户需求诊断")
async def cmd_needs_assessment(
    ctx,
    age: int = discord.SlashOption(description="年龄"),
    income: str = discord.SlashOption(description="年收入范围"),
    health_concerns: str = discord.SlashOption(description="健康关注点"),
):
    result = await mcp.call("needs_assessment", {
        "age": age, "income": income, "health_concerns": health_concerns
    })
    grade = result.get("grade", "?")
    summary = result.get("summary", "")
    await ctx.respond(f"**客户分级: {grade}**\n\n{summary}{DISCLAIMER}")

@bot.slash_command(name="product-query", description="保险产品查询")
async def cmd_product_query(
    ctx,
    product_id: str = discord.SlashOption(description="产品ID"),
    keyword: str = discord.SlashOption(description="搜索关键词"),
):
    result = await mcp.call("insurance_product_query", {
        "product_id": product_id or None,
        "keyword": keyword or None,
    })
    products = result.get("products", [])
    output = f"找到 {len(products)} 个产品:\n" + "\n---\n".join(
        json.dumps(p, indent=2, ensure_ascii=False) for p in products[:5]
    )
    await ctx.respond(output[:1800] + (f"\n...({len(products)} total)" if len(products) > 5 else "") + DISCLAIMER)

@bot.slash_command(name="objection-handling", description="异议处理话术生成")
async def cmd_objection_handling(
    ctx,
    objection: str = discord.SlashOption(description="客户异议"),
):
    result = await mcp.call("objection_handler", {"objection": objection})
    response_text = result.get("response", "") or json.dumps(result, ensure_ascii=False, indent=2)
    await ctx.respond(response_text + DISCLAIMER)

@bot.slash_command(name="private-sop", description="私域SOP生成")
async def cmd_private_sop(
    ctx,
    client_grade: str = discord.SlashOption(description="客户分级(A/B/C/D)", choices=["A","B","C","D"]),
):
    result = await mcp.call("private_sop_runner", {"grade": client_grade})
    output = json.dumps(result, ensure_ascii=False, indent=2)[:2000]
    await ctx.respond(f"**Day-0~Day-7 SOP for {client_grade}级客户:**\n\n{output}")

@bot.slash_command(name="help", description="查看可用命令")
async def cmd_help(ctx):
    slash_commands = [cmd.name for cmd in bot.tree.walk_application_commands()]
    output = "🏦 Insurance Advisor Bot 可用命令:\n" + "\n".join(f"/{c}" for c in sorted(slash_commands))
    await ctx.respond(output)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ 需要设置环境变量 DISCORD_TOKEN")
        print("   1. 前往 https://discord.com/developers/applications")
        print("   2. 创建App → Bot → Token")
        print("   3. 设置 export DISCORD_TOKEN=your_token")
        exit(1)
    bot.run(DISCORD_TOKEN)
