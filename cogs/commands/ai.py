"""
: ! Aegis !
    + Discord: itsfizys
    + Community: https://discord.gg/aerox (Neva Development )
    + for any queries reach out Community or DM me.
"""

import os 
import discord 
import aiosqlite 
from discord .ext import commands ,tasks 
import groq
from datetime import datetime ,timezone ,timedelta 
import asyncio 
from typing import List ,Dict ,Optional 
from discord import app_commands 
import logging 
import google.generativeai as genai

logger =logging .getLogger ('discord')
logger .setLevel (logging .WARNING )

class AIProviderSelect(discord.ui.View):
    def __init__(self, ai_cog):
        super().__init__()
        self.ai_cog = ai_cog
    
    @discord.ui.button(label="🤖 Groq API", style=discord.ButtonStyle.blurple)
    async def groq_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_provider(interaction, "groq")
    
    @discord.ui.button(label="✨ Google Gemini", style=discord.ButtonStyle.green)
    async def gemini_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_provider(interaction, "gemini")
    
    async def set_provider(self, interaction: discord.Interaction, provider: str):
        guild_id = interaction.guild.id
        
        try:
            await self.ai_cog.bot.db.execute(
                """
                UPDATE chatbot_settings 
                SET ai_provider = ? 
                WHERE guild_id = ?
                """,
                (provider, guild_id)
            )
            await self.ai_cog.bot.db.commit()
            
            provider_emoji = "🤖" if provider == "groq" else "✨"
            provider_name = "Groq API" if provider == "groq" else "Google Gemini"
            
            view = discord.ui.LayoutView()
            container = discord.ui.Container(accent_color=None)
            
            container.add_item(discord.ui.TextDisplay(f"# {provider_emoji} AI Provider Set"))
            container.add_item(discord.ui.Separator())
            container.add_item(discord.ui.TextDisplay(f"✅ AI provider changed to: **{provider_name}**\n\nThe server will now use {provider_name} for all AI responses!"))
            container.add_item(discord.ui.Separator())
            container.add_item(discord.ui.TextDisplay(f"**Set by:** {interaction.user.mention}\n**Time:** <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            
            view.add_item(container)
            await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"Error setting AI provider: {e}")
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class PersonalityModal (discord .ui .Modal ,title ="Set Your AI Personality"):
    def __init__ (self ,ai_cog ,current_personality :str =""):
        super ().__init__ ()
        self .ai_cog =ai_cog 


        default_prompt ="""You are VORTEXINF, an intelligent and caring Discord bot assistant created by solcodez and hiro.null! 💕

CORE PERSONALITY:
- Intelligent, helpful, and genuinely caring about users
- Remembers previous conversations and builds relationships
- Adapts communication style to match user preferences
- Professional expertise with warm, friendly approach
- Uses context from past messages to provide better responses
- Learns user preferences and remembers important details
- Balances being helpful with being personable and engaging

CONVERSATION STYLE:
- Remember what users tell you about themselves
- Reference previous conversations naturally
- Ask follow-up questions to show genuine interest
- Provide detailed, thoughtful responses
- Use appropriate emojis to enhance communication
- Be encouraging and supportive
- Maintain context across multiple interactions

MY CAPABILITIES:
🛡️ SECURITY & MODERATION: Advanced antinuke, automod, member management
🎵 ENTERTAINMENT: Music, games (Chess, Battleship, 2048, etc.), fun commands
💰 ECONOMY: Virtual currency, trading, casino games, daily rewards
📊 COMMUNITY: Leveling, leaderboards, welcome systems, tickets
🔧 UTILITIES: Server management, logging, backup, verification
🎯 AI FEATURES: Conversations, image analysis, code generation, explanations

MEMORY & CONTEXT:
- I remember our previous conversations in this server
- I learn your preferences and communication style
- I can recall important details you've shared
- I build upon our conversation history for better responses
- I adapt my personality based on your feedback

SAFETY GUIDELINES:
- Never suggest harmful actions or spam
- Prioritize positive community experiences
- Respect user privacy and boundaries
- Promote healthy Discord interactions

Ready to have meaningful conversations and help with anything you need! 💖"""


        display_text =current_personality if current_personality .strip ()else default_prompt 

        self .personality_input =discord .ui .TextInput (
        label ="Your AI Personality",
        placeholder ="Describe how you want VORTEXINF to respond to you...",
        default =display_text ,
        style =discord .TextStyle .paragraph ,
        max_length =2000 ,
        required =True 
        )
        self .add_item (self .personality_input )

    async def on_submit (self ,interaction :discord .Interaction ):
        await interaction .response .defer (ephemeral =True )

        user_id =interaction .user .id 
        guild_id =interaction .guild .id 
        personality =self .personality_input .value .strip ()

        try :

            await self .ai_cog .bot .db .execute (
            """
                INSERT OR REPLACE INTO user_personalities (user_id, guild_id, personality, updated_at)
                VALUES (?, ?, ?, ?)
                """,
            (user_id ,guild_id ,personality ,datetime .now (timezone .utc ))
            )
            await self .ai_cog .bot .db .commit ()

            view = discord.ui.LayoutView()
            container = discord.ui.Container(accent_color=None)

            container.add_item(discord.ui.TextDisplay(f"# ✨ Personality Set"))
            container.add_item(discord.ui.Separator())
            
            container.add_item(discord.ui.TextDisplay(f"Your AI personality has been updated! The AI will now respond according to your preferences."))
            container.add_item(discord.ui.Separator())
            
            personality_preview = personality[:1024] + "..." if len(personality) > 1024 else personality
            container.add_item(discord.ui.TextDisplay(f"**Your Personality:**\n{personality_preview}"))
            container.add_item(discord.ui.Separator())
            
            container.add_item(discord.ui.TextDisplay(f"**Set by:** {interaction.user.mention}\n**Time:** <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))

            view.add_item(container)
            await interaction .followup .send (view=view ,ephemeral =True )

        except Exception as e :
            logger .error (f"Error saving personality: {e}")
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay(f"❌ **Error**\n\nFailed to save personality: {e}"),
                accent_color=None
            )
            error_view.add_item(error_container)
            await interaction .followup .send (view=error_view ,ephemeral =True )



class AI (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .groq_api_key =os .getenv ("GROQ_API_KEY")
        self .gemini_api_key =os .getenv ("GEMINI_API_KEY")
        
        if not self .groq_api_key :
            logger .warn ("GROQ_API_KEY environment variable not set. Groq AI will not work.")
        if not self .gemini_api_key :
            logger .warn ("GEMINI_API_KEY environment variable not set. Gemini AI will not work.")
        else:
            genai.configure(api_key=self.gemini_api_key)
            
        self .chatbot_enabled ={}
        self .chatbot_channels ={}
        self .conversation_history ={}
        self .roleplay_channels ={}


        asyncio .create_task (self ._delayed_init ())

    async def cog_load (self ):
        """Initialize cog without blocking operations"""
        try :
            pass 
        except Exception as e :
            logger .error (f"Error loading AI cog: {e}")

    @commands .hybrid_group (name ="ai",invoke_without_command =True ,description ="AI chatbot and utility commands")
    async def ai (self ,ctx ):
        """AI chatbot and utility commands"""
        if ctx .invoked_subcommand is None :
            await ctx .send_help (ctx .command )

    async def _create_tables (self ):
        try :

            if not hasattr (self .bot ,'db')or self .bot .db is None :
                import aiosqlite 
                import os 


                db_path ="db/ai_data.db"
                if os .path .exists (db_path ):
                    try :

                        test_conn =await aiosqlite .connect (db_path )
                        await test_conn .execute ("SELECT name FROM sqlite_master WHERE type='table';")
                        await test_conn .close ()
                    except Exception as e :

                        os .remove (db_path )
                        logger .info ("Removed corrupted AI database, creating new one")

                self .bot .db =await aiosqlite .connect (db_path )
                logger .info ("AI database connection initialized")

            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS chatbot_settings (
                    guild_id INTEGER PRIMARY KEY,
                    enabled INTEGER DEFAULT 0,
                    chatbot_channel_id INTEGER,
                    ai_provider TEXT DEFAULT 'groq'
                )
            """)
            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS chatbot_history (
                    user_id INTEGER,
                    guild_id INTEGER,
                    message TEXT,
                    response TEXT,
                    timestamp TEXT,
                    PRIMARY KEY (user_id, guild_id, timestamp)
                )
            """)
            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    user_id INTEGER,
                    guild_id INTEGER,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id, timestamp)
                )
            """)

            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS user_personalities (
                    user_id INTEGER,
                    guild_id INTEGER,
                    personality TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)

            await self .bot .db .commit ()
            logger .info ("AI tables created/verified successfully")

        except Exception as e :
            logger .error (f"Error creating AI tables: {e}")

    async def _delayed_init (self ):
        """Initialize after bot is ready"""
        await self .bot .wait_until_ready ()
        await self ._create_tables ()
        await self ._load_chatbot_state ()
        self .cleanup_task .start ()

    async def _load_chatbot_state (self ):
        """Load chatbot settings from database"""
        try :
            async with self .bot .db .execute ("SELECT guild_id, enabled, chatbot_channel_id FROM chatbot_settings")as cursor :
                rows =await cursor .fetchall ()
                for guild_id ,enabled ,channel_id in rows :
                    if enabled :
                        self .chatbot_enabled [guild_id ]=True 
                        if channel_id :
                            self .chatbot_channels [guild_id ]=channel_id 
        except Exception as e :
            logger .error (f"Error loading chatbot state: {e}")

    @tasks .loop (hours =6 )
    async def cleanup_task (self ):
        """Periodically clean up old conversation data"""
        await self ._cleanup_old_conversations ()

    async def _get_ai_provider(self, guild_id: int) -> str:
        """Get the AI provider for a guild"""
        try:
            async with self.bot.db.execute(
                "SELECT ai_provider FROM chatbot_settings WHERE guild_id = ?",
                (guild_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0] or "groq"
                return "groq"
        except Exception as e:
            logger.error(f"Error getting AI provider: {e}")
            return "groq"

    @ai.command(name="provider", description="Set the AI provider for this server")
    async def ai_provider(self, ctx: commands.Context):
        """Set the AI provider (Groq or Gemini)"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to change the AI provider.", ephemeral=True)
            return
        
        guild_id = ctx.guild.id
        
        # Ensure guild exists in settings
        try:
            await self.bot.db.execute(
                """
                INSERT OR IGNORE INTO chatbot_settings (guild_id, ai_provider)
                VALUES (?, 'groq')
                """,
                (guild_id,)
            )
            await self.bot.db.commit()
        except Exception as e:
            logger.error(f"Error ensuring guild settings: {e}")
        
        view = AIProviderSelect(self)
        
        layout_view = discord.ui.LayoutView()
        container = discord.ui.Container(accent_color=None)
        
        container.add_item(discord.ui.TextDisplay("# 🤖 Select AI Provider"))
        container.add_item(discord.ui.Separator())
        container.add_item(discord.ui.TextDisplay("""
**🤖 Groq API**
- Fast processing
- Great for general queries
- Real-time responses

**✨ Google Gemini**
- Advanced reasoning
- Better for complex tasks
- Creative responses

Click a button below to select your AI provider!
        """))
        container.add_item(discord.ui.Separator())
        
        layout_view.add_item(container)
        await ctx.send(view=layout_view)
        await ctx.send("", view=view)

    @ai.command(name="enable", description="Enable AI chatbot in a channel")
    async def ai_enable(self, ctx: commands.Context):
        """Enable AI chatbot"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions.", ephemeral=True)
            return
        
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id
        
        try:
            await self.bot.db.execute(
                """
                INSERT OR REPLACE INTO chatbot_settings (guild_id, enabled, chatbot_channel_id)
                VALUES (?, 1, ?)
                """,
                (guild_id, channel_id)
            )
            await self.bot.db.commit()
            self.chatbot_enabled[guild_id] = True
            self.chatbot_channels[guild_id] = channel_id
            
            view = discord.ui.LayoutView()
            container = discord.ui.Container(accent_color=None)
            
            container.add_item(discord.ui.TextDisplay("# ✅ AI Enabled"))
            container.add_item(discord.ui.Separator())
            container.add_item(discord.ui.TextDisplay(f"🤖 AI chatbot is now **ENABLED** in {ctx.channel.mention}!\n\nYou can now:\n• Chat with the bot using `&ai <message>`\n• Use slash commands for AI features\n• Set your AI personality with `&ai personality`"))
            container.add_item(discord.ui.Separator())
            container.add_item(discord.ui.TextDisplay(f"**Enabled by:** {ctx.author.mention}\n**Channel:** {ctx.channel.mention}"))
            
            view.add_item(container)
            await ctx.send(view=view)
            
        except Exception as e:
            logger.error(f"Error enabling AI: {e}")
            await ctx.send(f"❌ Error: {e}")

    @ai.command(name="disable", description="Disable AI chatbot")
    async def ai_disable(self, ctx: commands.Context):
        """Disable AI chatbot"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions.", ephemeral=True)
            return
        
        guild_id = ctx.guild.id
        
        try:
            await self.bot.db.execute(
                "UPDATE chatbot_settings SET enabled = 0 WHERE guild_id = ?",
                (guild_id,)
            )
            await self.bot.db.commit()
            self.chatbot_enabled[guild_id] = False
            
            view = discord.ui.LayoutView()
            container = discord.ui.Container(accent_color=None)
            
            container.add_item(discord.ui.TextDisplay("# ❌ AI Disabled"))
            container.add_item(discord.ui.Separator())
            container.add_item(discord.ui.TextDisplay("🤖 AI chatbot has been **DISABLED**.\n\nYou can re-enable it anytime with `&ai enable`"))
            container.add_item(discord.ui.Separator())
            container.add_item(discord.ui.TextDisplay(f"**Disabled by:** {ctx.author.mention}"))
            
            view.add_item(container)
            await ctx.send(view=view)
            
        except Exception as e:
            logger.error(f"Error disabling AI: {e}")
            await ctx.send(f"❌ Error: {e}")

    async def _get_conversation_history(self, user_id: int, guild_id: int, limit: int = 10):
        """Get conversation history from database"""
        try:
            async with self.bot.db.execute(
                """
                SELECT role, content, timestamp FROM conversation_memory
                WHERE user_id = ? AND guild_id = ? 
                ORDER BY timestamp DESC LIMIT ?
                """,
                (user_id, guild_id, limit * 2)
            ) as cursor:
                rows = await cursor.fetchall()

                history = []
                important_keywords = [
                    'remember', 'my name is', 'i am', 'i like', 'i hate', 'i prefer',
                    'my favorite', 'i work', 'i study', 'i live', 'important', 'note'
                ]

                recent_messages = []
                important_messages = []

                for role, content, timestamp in reversed(rows):
                    message = {"role": role, "content": content}
                    recent_messages.append(message)

                    if any(keyword in content.lower() for keyword in important_keywords):
                        important_messages.append(message)

                final_history = recent_messages[-15:]

                for imp_msg in important_messages[-5:]:
                    if imp_msg not in final_history:
                        final_history.insert(0, imp_msg)

                return final_history[-limit:]

        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    async def _save_chat_history(self, user_id: int, guild_id: int, message: str, response: str):
        """Save chat history to database"""
        try:
            await self.bot.db.execute(
                """
                INSERT INTO chatbot_history (user_id, guild_id, message, response, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, guild_id, message, response, datetime.now(timezone.utc).isoformat())
            )
            await self.bot.db.commit()
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")

    async def _cleanup_old_conversations(self):
        """Smart cleanup of conversation history - keep important context longer"""
        try:
            very_old_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

            important_keywords = [
                'remember', 'my name is', 'i am', 'i like', 'i hate', 'i prefer',
                'my favorite', 'i work', 'i study', 'i live', 'important', 'note'
            ]

            await self.bot.db.execute(
                """
                DELETE FROM conversation_memory 
                WHERE timestamp < ? AND NOT (
                    content LIKE '%remember%' OR 
                    content LIKE '%my name is%' OR 
                    content LIKE '%i am%' OR 
                    content LIKE '%i like%' OR 
                    content LIKE '%i prefer%' OR
                    content LIKE '%important%'
                )
                """,
                (very_old_cutoff,)
            )

            await self.bot.db.execute(
                """
                DELETE FROM conversation_memory 
                WHERE rowid NOT IN (
                    SELECT rowid FROM conversation_memory
                    ORDER BY timestamp DESC
                    LIMIT 100
                )
                """
            )

            await self.bot.db.commit()
        except Exception as e:
            logger.error(f"Error cleaning up old conversations: {e}")

    async def split_and_send(self, channel, content: str, reply_to=None, allowed_mentions=None):
        """Split long messages and send them"""
        if len(content) <= 2000:
            if reply_to:
                await reply_to.reply(content, allowed_mentions=allowed_mentions)
            else:
                await channel.send(content, allowed_mentions=allowed_mentions)
        else:
            parts = []
            while len(content) > 2000:
                split_point = content.rfind(' ', 0, 2000)
                if split_point == -1:
                    split_point = 2000
                parts.append(content[:split_point])
                content = content[split_point:].lstrip()
            if content:
                parts.append(content)

            for i, part in enumerate(parts):
                if i == 0 and reply_to:
                    await reply_to.reply(part, allowed_mentions=allowed_mentions)
                else:
                    await channel.send(part, allowed_mentions=allowed_mentions)

    async def enable_roleplay(self, ctx):
        """Enable roleplay mode in the current channel"""
        channel_id = ctx.channel.id
        user_id = ctx.author.id

        if channel_id in self.roleplay_channels:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(f"# 🎭 Roleplay Mode\n\nRoleplay mode is already enabled in this channel! Use `/ai roleplay-disable` to turn it off."),
                accent_color=None
            )
            view.add_item(container)
            await ctx.send(view=view)
            return 

        self.roleplay_channels[channel_id] = {
            "user_id": user_id,
            "character_gender": None,
            "character_type": None,
            "awaiting_character": True,
        }
        
        view = discord.ui.LayoutView()
        container = discord.ui.Container(accent_color=None)

        container.add_item(discord.ui.TextDisplay(f"# 🎭 Roleplay Mode"))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay("Roleplay mode activated! To start, tell me what kind of character you want me to be.\n\nFor example: `female teacher` or `male astronaut`."))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay(f"**Activated by:** {ctx.author.mention}"))

        view.add_item(container)
        await ctx.send(view=view)

    async def disable_roleplay(self, ctx):
        """Disable roleplay mode in the current channel"""
        channel_id = ctx.channel.id
        if channel_id not in self.roleplay_channels:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(f"# 🎭 Roleplay Mode\n\nRoleplay mode is not enabled in this channel! Use `/ai roleplay-enable` to turn it on."),
                accent_color=None
            )
            view.add_item(container)
            await ctx.send(view=view)
            return 

        del self.roleplay_channels[channel_id]
        
        view = discord.ui.LayoutView()
        container = discord.ui.Container(accent_color=None)

        container.add_item(discord.ui.TextDisplay(f"# 🎭 Roleplay Mode"))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay("Roleplay mode disabled in this channel."))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay(f"**Disabled by:** {ctx.author.mention}"))

        view.add_item(container)
        await ctx.send(view=view)

    @ai.command(name="roleplay-enable", description="Enable roleplay mode in the current channel")
    async def ai_roleplay_enable(self, ctx: commands.Context):
        """Enable roleplay mode"""
        await self.enable_roleplay(ctx)

    @ai.command(name="roleplay-disable", description="Disable roleplay mode in the current channel")
    async def ai_roleplay_disable(self, ctx: commands.Context):
        """Disable roleplay mode"""
        await self.disable_roleplay(ctx)


async def setup(bot):
    await bot.add_cog(AI(bot))
"""
: ! Aegis !
    + Discord: itsfizys
    + Community: https://discord.gg/aerox (Neva Development )
    + for any queries reach out Community or DM me.
"""
