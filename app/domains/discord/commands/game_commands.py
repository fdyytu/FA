"""
Discord bot commands untuk fitur gaming
"""
import discord
from discord.ext import commands
from typing import Optional
import asyncio
from app.domains.game.services.game_service import GameValidationService, GameProductService
from app.domains.game.schemas.game_schemas import GameValidationRequest
from app.core.database import get_db

class GameCommands(commands.Cog):
    """Commands untuk fitur gaming"""
    
    def __init__(self, bot):
        self.bot = bot
        self.validation_service = GameValidationService()
    
    @commands.slash_command(name="cek", description="Cek nickname/validasi akun game")
    async def cek_akun(self, ctx, game: str, userid: str, server: str = None):
        """Command untuk validasi akun game"""
        await ctx.defer()
        
        try:
            request = GameValidationRequest(
                game_code=game.upper(),
                user_id=userid,
                server_id=server
            )
            
            result = await self.validation_service.validate_game_account(request)
            
            embed = discord.Embed(
                title=f"🎮 Validasi Akun {game.upper()}",
                color=0x00ff00 if result.is_valid else 0xff0000
            )
            
            embed.add_field(name="User ID", value=result.user_id, inline=True)
            if result.server_id:
                embed.add_field(name="Server", value=result.server_id, inline=True)
            if result.nickname:
                embed.add_field(name="Nickname", value=result.nickname, inline=True)
            
            status = "✅ Valid" if result.is_valid else "❌ Invalid"
            embed.add_field(name="Status", value=status, inline=False)
            embed.add_field(name="Pesan", value=result.message, inline=False)
            
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            await ctx.followup.send(f"❌ Error: {str(e)}")
    
    @commands.slash_command(name="price", description="Lihat daftar harga produk game")
    async def price_list(self, ctx, game: str):
        """Command untuk melihat daftar harga"""
        await ctx.defer()
        
        try:
            prices = {
                "ML": [
                    "• 86 Diamond: Rp 20,000",
                    "• 172 Diamond: Rp 40,000", 
                    "• 257 Diamond: Rp 60,000"
                ],
                "FF": [
                    "• 70 Diamond: Rp 10,000",
                    "• 140 Diamond: Rp 20,000"
                ]
            }
            
            game_prices = prices.get(game.upper(), ["Harga belum tersedia"])
            
            embed = discord.Embed(
                title=f"💰 Daftar Harga {game.upper()}",
                description="\n".join(game_prices),
                color=0x0099ff
            )
            
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            await ctx.followup.send(f"❌ Error: {str(e)}")
