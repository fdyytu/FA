"""
Discord Bot Slash Commands
Mengelola semua slash commands untuk Discord bot
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional
from decimal import Decimal

from app.infrastructure.database.database_manager import get_db
from app.models.discord import (
    DiscordUser, DiscordWallet, LiveStock, 
    AdminWorldConfig, CurrencyType
)

logger = logging.getLogger(__name__)


class DiscordSlashCommands:
    """Service untuk mengelola Discord Slash Commands"""
    
    def __init__(self, bot: commands.Bot, bot_config):
        self.bot = bot
        self.bot_config = bot_config
        
    async def setup_commands(self):
        """Setup Discord slash commands"""
        
        @self.bot.tree.command(name="buy", description="Beli produk dari live stock")
        @app_commands.describe(
            product_code="Kode produk yang ingin dibeli",
            quantity="Jumlah yang ingin dibeli",
            currency="Mata uang pembayaran (WL/DL/BGL)"
        )
        async def buy_command(
            interaction: discord.Interaction,
            product_code: str,
            quantity: int,
            currency: str = "WL"
        ):
            await self._handle_buy_command(interaction, product_code, quantity, currency)
        
        @self.bot.tree.command(name="growid", description="Set atau lihat Grow ID")
        @app_commands.describe(grow_id="Grow ID untuk disimpan (kosongkan untuk melihat)")
        async def growid_command(interaction: discord.Interaction, grow_id: str = None):
            await self._handle_growid_command(interaction, grow_id)
        
        @self.bot.tree.command(name="balance", description="Lihat saldo wallet")
        async def balance_command(interaction: discord.Interaction):
            await self._handle_balance_command(interaction)
        
        @self.bot.tree.command(name="world", description="Lihat daftar world admin")
        async def world_command(interaction: discord.Interaction):
            await self._handle_world_command(interaction)
    
    async def _handle_buy_command(
        self, 
        interaction: discord.Interaction, 
        product_code: str, 
        quantity: int, 
        currency: str
    ):
        """Handle buy command"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            db = next(get_db())
            
            # Validate currency
            if currency.upper() not in ["WL", "DL", "BGL"]:
                await interaction.followup.send(
                    "❌ Mata uang tidak valid. Gunakan WL, DL, atau BGL",
                    ephemeral=True
                )
                return
            
            # Get or create discord user
            discord_user = db.query(DiscordUser).filter(
                DiscordUser.discord_id == str(interaction.user.id)
            ).first()
            
            if not discord_user:
                await interaction.followup.send(
                    "❌ Anda belum terdaftar. Silakan set Grow ID terlebih dahulu dengan `/growid`",
                    ephemeral=True
                )
                return
            
            # Find product in live stock
            product = db.query(LiveStock).filter(
                LiveStock.product_code == product_code.upper(),
                LiveStock.is_active == True,
                LiveStock.stock >= quantity
            ).first()
            
            if not product:
                await interaction.followup.send(
                    f"❌ Produk {product_code} tidak tersedia atau stok tidak mencukupi",
                    ephemeral=True
                )
                return
            
            # Calculate total price
            total_price = product.price * quantity
            
            # Get user wallet
            wallet = db.query(DiscordWallet).filter(
                DiscordWallet.discord_user_id == discord_user.id
            ).first()
            
            if not wallet:
                await interaction.followup.send(
                    "❌ Wallet tidak ditemukan",
                    ephemeral=True
                )
                return
            
            # Check balance based on currency
            currency_balance = getattr(wallet, f"{currency.lower()}_balance")
            if currency_balance < total_price:
                await interaction.followup.send(
                    f"❌ Saldo {currency.upper()} tidak mencukupi. "
                    f"Dibutuhkan: {total_price:,.2f}, Tersedia: {currency_balance:,.2f}",
                    ephemeral=True
                )
                return
            
            # Process purchase
            # Deduct balance
            setattr(wallet, f"{currency.lower()}_balance", currency_balance - total_price)
            
            # Reduce stock
            product.stock -= quantity
            
            db.commit()
            
            # Send success message
            embed = discord.Embed(
                title="✅ Pembelian Berhasil",
                color=discord.Color.green()
            )
            embed.add_field(name="Produk", value=product.product_name, inline=True)
            embed.add_field(name="Jumlah", value=f"{quantity:,}", inline=True)
            embed.add_field(name="Total", value=f"{total_price:,.2f} {currency.upper()}", inline=True)
            embed.add_field(name="Sisa Stok", value=f"{product.stock:,}", inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in buy command: {e}")
            await interaction.followup.send(
                "❌ Terjadi kesalahan saat memproses pembelian",
                ephemeral=True
            )
    
    async def _handle_growid_command(self, interaction: discord.Interaction, grow_id: str = None):
        """Handle growid command"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            db = next(get_db())
            
            # Get or create discord user
            discord_user = db.query(DiscordUser).filter(
                DiscordUser.discord_id == str(interaction.user.id)
            ).first()
            
            if grow_id:
                # Set new grow ID
                if not discord_user:
                    # Create new user
                    discord_user = DiscordUser(
                        discord_id=str(interaction.user.id),
                        username=interaction.user.name,
                        grow_id=grow_id
                    )
                    db.add(discord_user)
                    
                    # Create wallet
                    wallet = DiscordWallet(discord_user=discord_user)
                    db.add(wallet)
                else:
                    # Update existing user
                    discord_user.grow_id = grow_id
                
                db.commit()
                
                await interaction.followup.send(
                    f"✅ Grow ID berhasil diset: `{grow_id}`",
                    ephemeral=True
                )
            else:
                # Show current grow ID
                if discord_user and discord_user.grow_id:
                    await interaction.followup.send(
                        f"🌱 Grow ID Anda: `{discord_user.grow_id}`",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Anda belum mengatur Grow ID. Gunakan `/growid <grow_id>` untuk mengatur",
                        ephemeral=True
                    )
                    
        except Exception as e:
            logger.error(f"Error in growid command: {e}")
            await interaction.followup.send(
                "❌ Terjadi kesalahan saat memproses Grow ID",
                ephemeral=True
            )
    
    async def _handle_balance_command(self, interaction: discord.Interaction):
        """Handle balance command"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            db = next(get_db())
            
            # Get discord user
            discord_user = db.query(DiscordUser).filter(
                DiscordUser.discord_id == str(interaction.user.id)
            ).first()
            
            if not discord_user:
                await interaction.followup.send(
                    "❌ Anda belum terdaftar. Silakan set Grow ID terlebih dahulu dengan `/growid`",
                    ephemeral=True
                )
                return
            
            # Get wallet
            wallet = db.query(DiscordWallet).filter(
                DiscordWallet.discord_user_id == discord_user.id
            ).first()
            
            if not wallet:
                await interaction.followup.send(
                    "❌ Wallet tidak ditemukan",
                    ephemeral=True
                )
                return
            
            # Calculate total in WL equivalent (example conversion rates)
            dl_to_wl = 100  # 1 DL = 100 WL
            bgl_to_wl = 10000  # 1 BGL = 10000 WL
            
            total_wl = (
                wallet.wl_balance + 
                (wallet.dl_balance * dl_to_wl) + 
                (wallet.bgl_balance * bgl_to_wl)
            )
            
            # Create embed
            embed = discord.Embed(
                title="💰 Saldo Wallet",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="World Lock (WL)",
                value=f"{wallet.wl_balance:,.2f}",
                inline=True
            )
            
            embed.add_field(
                name="Diamond Lock (DL)",
                value=f"{wallet.dl_balance:,.2f}",
                inline=True
            )
            
            embed.add_field(
                name="Blue Gem Lock (BGL)",
                value=f"{wallet.bgl_balance:,.2f}",
                inline=True
            )
            
            embed.add_field(
                name="Total (WL Equivalent)",
                value=f"{total_wl:,.2f} WL",
                inline=False
            )
            
            if discord_user.grow_id:
                embed.add_field(
                    name="Grow ID",
                    value=discord_user.grow_id,
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in balance command: {e}")
            await interaction.followup.send(
                "❌ Terjadi kesalahan saat mengambil saldo",
                ephemeral=True
            )
    
    async def _handle_world_command(self, interaction: discord.Interaction):
        """Handle world command"""
        try:
            await interaction.response.defer()
            
            db = next(get_db())
            
            # Get active worlds
            worlds = db.query(AdminWorldConfig).filter(
                AdminWorldConfig.is_active == True
            ).all()
            
            if not worlds:
                embed = discord.Embed(
                    title="❌ Tidak Ada World",
                    description="Belum ada world yang dikonfigurasi admin",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create embed with world list
            embed = discord.Embed(
                title="🌍 Daftar World Admin",
                color=discord.Color.green()
            )
            
            for world in worlds:
                embed.add_field(
                    name=f"🌍 {world.world_name}",
                    value=f"Admin: {world.admin_name}\nStatus: {'🟢 Aktif' if world.is_active else '🔴 Tidak Aktif'}",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in world command: {e}")
            await interaction.followup.send(
                "❌ Terjadi kesalahan saat mengambil daftar world"
            )
