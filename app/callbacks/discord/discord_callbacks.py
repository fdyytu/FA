"""
Discord Bot Event Handlers
Mengelola event callbacks dari Discord bot
"""
from typing import Dict, Any, Callable
import discord
from discord.ext import commands
import logging

from app.callbacks.base.base_handlers import EventCallbackHandler

logger = logging.getLogger(__name__)


class DiscordBotEventHandler(EventCallbackHandler):
    """Handler untuk Discord bot events"""
    
    def __init__(self, bot: commands.Bot):
        super().__init__("DiscordBotEvents", "discord_bot")
        self.bot = bot
        self._setup_event_handlers()
    
    async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Discord bot events"""
        event_type = data.get('event_type')
        event_data = data.get('event_data', {})
        
        if event_type == 'on_ready':
            return await self._handle_on_ready(event_data)
        elif event_type == 'on_message':
            return await self._handle_on_message(event_data)
        elif event_type == 'on_command_error':
            return await self._handle_command_error(event_data)
        elif event_type == 'on_member_join':
            return await self._handle_member_join(event_data)
        elif event_type == 'on_member_remove':
            return await self._handle_member_remove(event_data)
        else:
            logger.warning(f"Unknown Discord event type: {event_type}")
            return {'success': False, 'message': f'Unknown event type: {event_type}'}
    
    def _setup_event_handlers(self):
        """Setup Discord bot event handlers"""
        
        @self.bot.event
        async def on_ready():
            """Bot ready event"""
            await self.process_event({
                'event_type': 'on_ready',
                'event_data': {
                    'bot_user': str(self.bot.user),
                    'guild_count': len(self.bot.guilds)
                }
            })
        
        @self.bot.event
        async def on_message(message):
            """Message received event"""
            if message.author == self.bot.user:
                return
            
            await self.process_event({
                'event_type': 'on_message',
                'event_data': {
                    'author': str(message.author),
                    'content': message.content,
                    'guild': str(message.guild) if message.guild else 'DM',
                    'channel': str(message.channel)
                }
            })
            
            # Process commands
            await self.bot.process_commands(message)
        
        @self.bot.event
        async def on_command_error(ctx, error):
            """Command error event"""
            await self.process_event({
                'event_type': 'on_command_error',
                'event_data': {
                    'command': ctx.command.name if ctx.command else 'Unknown',
                    'error': str(error),
                    'author': str(ctx.author),
                    'guild': str(ctx.guild) if ctx.guild else 'DM'
                }
            })
        
        @self.bot.event
        async def on_member_join(member):
            """Member join event"""
            await self.process_event({
                'event_type': 'on_member_join',
                'event_data': {
                    'member': str(member),
                    'guild': str(member.guild),
                    'member_count': member.guild.member_count
                }
            })
        
        @self.bot.event
        async def on_member_remove(member):
            """Member remove event"""
            await self.process_event({
                'event_type': 'on_member_remove',
                'event_data': {
                    'member': str(member),
                    'guild': str(member.guild),
                    'member_count': member.guild.member_count
                }
            })
    
    async def _handle_on_ready(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bot ready event"""
        try:
            bot_user = event_data.get('bot_user')
            guild_count = event_data.get('guild_count', 0)
            
            logger.info(f"Discord bot {bot_user} is ready! Connected to {guild_count} guilds")
            
            # Start periodic tasks jika ada
            await self._start_periodic_tasks()
            
            # Sync slash commands
            try:
                synced = await self.bot.tree.sync()
                logger.info(f"Synced {len(synced)} slash commands")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}")
            
            return {
                'success': True,
                'message': f'Bot ready with {guild_count} guilds',
                'synced_commands': len(synced) if 'synced' in locals() else 0
            }
            
        except Exception as e:
            logger.error(f"Error handling on_ready event: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_on_message(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle message event"""
        try:
            author = event_data.get('author')
            content = event_data.get('content')
            guild = event_data.get('guild')
            
            # Log message (optional, bisa di-filter untuk privacy)
            if not content.startswith('!'):  # Don't log commands
                logger.debug(f"Message from {author} in {guild}: {content[:50]}...")
            
            # Bisa tambahkan logic untuk auto-response, moderation, etc.
            
            return {'success': True, 'message': 'Message processed'}
            
        except Exception as e:
            logger.error(f"Error handling message event: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_command_error(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle command error event"""
        try:
            command = event_data.get('command')
            error = event_data.get('error')
            author = event_data.get('author')
            
            logger.error(f"Command error - Command: {command}, User: {author}, Error: {error}")
            
            # Bisa kirim notifikasi ke admin atau log ke database
            
            return {'success': True, 'message': 'Command error logged'}
            
        except Exception as e:
            logger.error(f"Error handling command error event: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_member_join(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle member join event"""
        try:
            member = event_data.get('member')
            guild = event_data.get('guild')
            member_count = event_data.get('member_count')
            
            logger.info(f"New member {member} joined {guild}. Total members: {member_count}")
            
            # Bisa kirim welcome message, assign role, etc.
            
            return {'success': True, 'message': 'Member join processed'}
            
        except Exception as e:
            logger.error(f"Error handling member join event: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_member_remove(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle member remove event"""
        try:
            member = event_data.get('member')
            guild = event_data.get('guild')
            member_count = event_data.get('member_count')
            
            logger.info(f"Member {member} left {guild}. Total members: {member_count}")
            
            # Bisa log ke database, kirim notifikasi, etc.
            
            return {'success': True, 'message': 'Member remove processed'}
            
        except Exception as e:
            logger.error(f"Error handling member remove event: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _start_periodic_tasks(self):
        """Start periodic tasks untuk bot"""
        try:
            # Import dan start live stock update task
            from app.domains.discord.services.bot.bot_events import DiscordBotEvents
            
            # Bisa tambahkan periodic tasks lainnya di sini
            logger.info("Discord bot periodic tasks started")
            
        except Exception as e:
            logger.error(f"Error starting periodic tasks: {str(e)}")


class DiscordSlashCommandHandler(EventCallbackHandler):
    """Handler untuk Discord slash commands"""
    
    def __init__(self, bot: commands.Bot):
        super().__init__("DiscordSlashCommands", "discord_slash")
        self.bot = bot
        self._setup_slash_commands()
    
    async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle slash command events"""
        command_name = data.get('command_name')
        interaction_data = data.get('interaction_data', {})
        
        # Process slash command
        logger.info(f"Slash command executed: {command_name}")
        
        return {'success': True, 'message': f'Slash command {command_name} processed'}
    
    def _setup_slash_commands(self):
        """Setup slash commands"""
        
        @self.bot.tree.command(name="ping", description="Check bot latency")
        async def ping(interaction: discord.Interaction):
            """Ping command"""
            latency = round(self.bot.latency * 1000)
            await interaction.response.send_message(f"Pong! Latency: {latency}ms")
            
            # Log command usage
            await self.process_event({
                'command_name': 'ping',
                'interaction_data': {
                    'user': str(interaction.user),
                    'guild': str(interaction.guild) if interaction.guild else 'DM',
                    'latency': latency
                }
            })
        
        @self.bot.tree.command(name="info", description="Get bot information")
        async def info(interaction: discord.Interaction):
            """Info command"""
            embed = discord.Embed(
                title="Bot Information",
                description="FA Backend Discord Bot",
                color=discord.Color.blue()
            )
            embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
            embed.add_field(name="Users", value=len(self.bot.users), inline=True)
            embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
            # Log command usage
            await self.process_event({
                'command_name': 'info',
                'interaction_data': {
                    'user': str(interaction.user),
                    'guild': str(interaction.guild) if interaction.guild else 'DM'
                }
            })
