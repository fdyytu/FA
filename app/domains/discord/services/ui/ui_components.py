"""
Discord Bot UI Components
Mengelola semua UI components seperti buttons, modals, views
"""

import discord
from discord.ext import commands
import logging
from typing import Optional

from app.core.database import get_db
from app.models.discord import DiscordUser, DiscordWallet

logger = logging.getLogger(__name__)


class MainMenuView(discord.ui.View):
    """Main menu view dengan buttons"""
    
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🛒 Beli Produk", style=discord.ButtonStyle.primary, custom_id="buy_button")
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BuyModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🌱 Grow ID", style=discord.ButtonStyle.blurple, custom_id="growid_button")
    async def growid_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = GrowIDModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="💰 Balance", style=discord.ButtonStyle.gray, custom_id="balance_button")
    async def balance_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            db = next(get_db())
            
            # Get discord user
            discord_user = db.query(DiscordUser).filter(
                DiscordUser.discord_id == str(interaction.user.id)
            ).first()
            
            if not discord_user:
                await interaction.followup.send(
                    "❌ Anda belum terdaftar. Silakan set Grow ID terlebih dahulu",
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
            
            # Create balance embed
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
            
            if discord_user.grow_id:
                embed.add_field(
                    name="Grow ID",
                    value=discord_user.grow_id,
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in balance button: {e}")
            await interaction.followup.send(
                "❌ Terjadi kesalahan saat mengambil saldo",
                ephemeral=True
            )
    
    @discord.ui.button(label="🌍 World", style=discord.ButtonStyle.secondary, custom_id="world_button")
    async def world_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        try:
            from app.models.discord import AdminWorldConfig
            
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
            logger.error(f"Error in world button: {e}")
            await interaction.followup.send(
                "❌ Terjadi kesalahan saat mengambil daftar world"
            )


class BuyModal(discord.ui.Modal, title="Beli Produk"):
    """Modal untuk pembelian produk"""
    
    product_code = discord.ui.TextInput(
        label="Kode Produk",
        placeholder="Masukkan kode produk...",
        required=True,
        max_length=100
    )
    
    quantity = discord.ui.TextInput(
        label="Jumlah",
        placeholder="Masukkan jumlah...",
        required=True,
        max_length=10
    )
    
    currency = discord.ui.TextInput(
        label="Mata Uang (WL/DL/BGL)",
        placeholder="WL",
        required=False,
        max_length=3,
        default="WL"
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            quantity_int = int(self.quantity.value)
            currency_str = self.currency.value.upper() or "WL"
            
            await interaction.response.defer(ephemeral=True)
            
            # Import here to avoid circular imports
            from app.domains.discord.services.commands.slash_commands import DiscordSlashCommands
            
            # Create temporary command handler
            command_handler = DiscordSlashCommands(None, None)
            await command_handler._handle_buy_command(
                interaction, 
                self.product_code.value, 
                quantity_int, 
                currency_str
            )
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Jumlah harus berupa angka",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in buy modal: {e}")
            await interaction.response.send_message(
                "❌ Terjadi kesalahan saat memproses pembelian",
                ephemeral=True
            )


class GrowIDModal(discord.ui.Modal, title="Set Grow ID"):
    """Modal untuk mengatur Grow ID"""
    
    grow_id = discord.ui.TextInput(
        label="Grow ID",
        placeholder="Masukkan Grow ID Anda...",
        required=True,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            
            db = next(get_db())
            
            # Get or create discord user
            discord_user = db.query(DiscordUser).filter(
                DiscordUser.discord_id == str(interaction.user.id)
            ).first()
            
            if not discord_user:
                # Create new user
                discord_user = DiscordUser(
                    discord_id=str(interaction.user.id),
                    username=interaction.user.name,
                    grow_id=self.grow_id.value
                )
                db.add(discord_user)
                
                # Create wallet
                wallet = DiscordWallet(discord_user=discord_user)
                db.add(wallet)
            else:
                # Update existing user
                discord_user.grow_id = self.grow_id.value
            
            db.commit()
            
            await interaction.followup.send(
                f"✅ Grow ID berhasil diset: `{self.grow_id.value}`",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error in grow ID modal: {e}")
            await interaction.followup.send(
                "❌ Terjadi kesalahan saat mengatur Grow ID",
                ephemeral=True
            )


class StockListView(discord.ui.View):
    """View untuk menampilkan daftar stock dengan pagination"""
    
    def __init__(self, stocks, page=0, per_page=5):
        super().__init__(timeout=300)
        self.stocks = stocks
        self.page = page
        self.per_page = per_page
        self.max_page = (len(stocks) - 1) // per_page
        
        # Update button states
        self.previous_page.disabled = page == 0
        self.next_page.disabled = page >= self.max_page
    
    def get_current_page_embed(self):
        """Get embed for current page"""
        start_idx = self.page * self.per_page
        end_idx = start_idx + self.per_page
        current_stocks = self.stocks[start_idx:end_idx]
        
        embed = discord.Embed(
            title="📦 Live Stock",
            description=f"Halaman {self.page + 1}/{self.max_page + 1}",
            color=discord.Color.blue()
        )
        
        for stock in current_stocks:
            embed.add_field(
                name=f"{stock.product_code} - {stock.product_name}",
                value=f"Harga: {stock.price:,.2f} WL\nStok: {stock.stock:,}",
                inline=True
            )
        
        return embed
    
    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.gray)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.previous_page.disabled = self.page == 0
        self.next_page.disabled = False
        
        embed = self.get_current_page_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="▶️ Next", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.next_page.disabled = self.page >= self.max_page
        self.previous_page.disabled = False
        
        embed = self.get_current_page_embed()
        await interaction.response.edit_message(embed=embed, view=self)
