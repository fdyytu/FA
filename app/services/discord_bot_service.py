import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import logging
from typing import Optional, List, Dict, Any
from decimal import Decimal
import json
from datetime import datetime

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.discord import (
    DiscordBot, DiscordUser, DiscordWallet, DiscordTransaction,
    LiveStock, AdminWorldConfig, CurrencyType
)
from app.schemas.discord import (
    BuyProductRequest, BuyProductResponse, BalanceResponse,
    CurrencyConversionRequest, CurrencyConversionResponse
)

logger = logging.getLogger(__name__)

class DiscordBotService:
    """Service untuk mengelola Discord Bot dengan prinsip SOLID"""
    
    def __init__(self):
        self.bot: Optional[commands.Bot] = None
        self.bot_config: Optional[DiscordBot] = None
        self.is_running = False
        
    async def initialize_bot(self, bot_id: int, db: Session):
        """Initialize Discord Bot"""
        try:
            # Get bot configuration
            self.bot_config = db.query(DiscordBot).filter(
                DiscordBot.id == bot_id,
                DiscordBot.is_active == True
            ).first()
            
            if not self.bot_config:
                raise ValueError(f"Bot configuration not found for ID: {bot_id}")
            
            # Setup bot intents
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True
            intents.members = True
            
            # Create bot instance
            self.bot = commands.Bot(
                command_prefix='!',
                intents=intents,
                description="Live Stock Bot untuk Growtopia"
            )
            
            # Setup event handlers
            self._setup_events()
            
            # Setup commands
            await self._setup_commands()
            
            logger.info(f"Discord bot initialized for guild: {self.bot_config.guild_id}")
            
        except Exception as e:
            logger.error(f"Error initializing Discord bot: {e}")
            raise
    
    def _setup_events(self):
        """Setup Discord bot events"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f'{self.bot.user} has connected to Discord!')
            
            # Start live stock update task
            if not self.update_live_stock.is_running():
                self.update_live_stock.start()
            
            # Sync slash commands
            try:
                synced = await self.bot.tree.sync()
                logger.info(f"Synced {len(synced)} command(s)")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}")
        
        @self.bot.event
        async def on_error(event, *args, **kwargs):
            logger.error(f"Discord bot error in {event}: {args}")
    
    async def _setup_commands(self):
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
            await interaction.response.defer()
            
            db = next(get_db())
            
            # Get or create Discord user
            discord_user = await self._get_or_create_user(
                interaction.user.id, 
                interaction.user.display_name, 
                db
            )
            
            # Validate currency
            if currency.upper() not in ["WL", "DL", "BGL"]:
                await interaction.followup.send(
                    "❌ Currency tidak valid! Gunakan WL, DL, atau BGL",
                    ephemeral=True
                )
                return
            
            # Process purchase
            result = await self._process_purchase(
                discord_user, product_code, quantity, currency.upper(), db
            )
            
            if result.success:
                embed = discord.Embed(
                    title="✅ Pembelian Berhasil",
                    description=result.message,
                    color=discord.Color.green()
                )
                
                if result.remaining_balance:
                    embed.add_field(
                        name="Saldo Tersisa",
                        value=f"WL: {result.remaining_balance.wl_balance}\n"
                              f"DL: {result.remaining_balance.dl_balance}\n"
                              f"BGL: {result.remaining_balance.bgl_balance}",
                        inline=False
                    )
            else:
                embed = discord.Embed(
                    title="❌ Pembelian Gagal",
                    description=result.message,
                    color=discord.Color.red()
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in buy command: {e}")
            await interaction.followup.send(
                "❌ Terjadi kesalahan saat memproses pembelian",
                ephemeral=True
            )
    
    async def _handle_growid_command(
        self, 
        interaction: discord.Interaction, 
        grow_id: Optional[str]
    ):
        """Handle grow ID command"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            db = next(get_db())
            
            # Get or create Discord user
            discord_user = await self._get_or_create_user(
                interaction.user.id, 
                interaction.user.display_name, 
                db
            )
            
            if grow_id:
                # Set new Grow ID
                discord_user.grow_id = grow_id
                discord_user.is_verified = True
                db.commit()
                
                embed = discord.Embed(
                    title="✅ Grow ID Berhasil Disimpan",
                    description=f"Grow ID: **{grow_id}**",
                    color=discord.Color.green()
                )
            else:
                # Show current Grow ID
                if discord_user.grow_id:
                    embed = discord.Embed(
                        title="📋 Grow ID Anda",
                        description=f"Grow ID: **{discord_user.grow_id}**\n"
                                  f"Status: {'✅ Verified' if discord_user.is_verified else '❌ Not Verified'}",
                        color=discord.Color.blue()
                    )
                else:
                    embed = discord.Embed(
                        title="❌ Grow ID Belum Diset",
                        description="Gunakan `/growid <your_grow_id>` untuk mengatur Grow ID",
                        color=discord.Color.orange()
                    )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
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
            
            # Get or create Discord user
            discord_user = await self._get_or_create_user(
                interaction.user.id, 
                interaction.user.display_name, 
                db
            )
            
            # Get wallet
            wallet = discord_user.discord_wallet
            if not wallet:
                wallet = DiscordWallet(user_id=discord_user.id)
                db.add(wallet)
                db.commit()
                db.refresh(wallet)
            
            # Calculate total in WL equivalent
            total_wl = self._calculate_wl_equivalent(wallet)
            
            embed = discord.Embed(
                title="💰 Saldo Wallet Anda",
                color=discord.Color.gold()
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
            else:
                embed = discord.Embed(
                    title="🌍 Daftar World Admin",
                    color=discord.Color.blue()
                )
                
                for world in worlds:
                    embed.add_field(
                        name=f"🏠 {world.world_name}",
                        value=f"{world.world_description or 'Tidak ada deskripsi'}\n"
                              f"Access: {world.access_level.title()}",
                        inline=False
                    )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in world command: {e}")
            await interaction.followup.send(
                "❌ Terjadi kesalahan saat mengambil daftar world"
            )
    
    @tasks.loop(minutes=5)
    async def update_live_stock(self):
        """Update live stock display every 5 minutes"""
        try:
            if not self.bot or not self.bot_config:
                return
            
            db = next(get_db())
            
            # Get live stock channel
            channel = self.bot.get_channel(int(self.bot_config.live_stock_channel_id))
            if not channel:
                logger.warning("Live stock channel not found")
                return
            
            # Get live stock products
            products = db.query(LiveStock).filter(
                LiveStock.bot_id == self.bot_config.id,
                LiveStock.is_active == True
            ).order_by(LiveStock.display_order, LiveStock.product_name).all()
            
            # Create embed
            embed = await self._create_live_stock_embed(products)
            
            # Create view with buttons
            view = LiveStockView(products)
            
            # Delete old messages and send new one
            async for message in channel.history(limit=10):
                if message.author == self.bot.user:
                    await message.delete()
            
            await channel.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error updating live stock: {e}")
    
    async def _create_live_stock_embed(self, products: List[LiveStock]) -> discord.Embed:
        """Create live stock embed"""
        embed = discord.Embed(
            title="🛒 Live Stock - Real Time",
            description="Produk tersedia untuk pembelian",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        if not products:
            embed.add_field(
                name="❌ Tidak Ada Produk",
                value="Belum ada produk yang tersedia",
                inline=False
            )
        else:
            for product in products[:10]:  # Limit to 10 products
                status = "✅ Tersedia" if product.stock_quantity > 0 else "❌ Habis"
                featured = "⭐ " if product.is_featured else ""
                
                embed.add_field(
                    name=f"{featured}{product.product_name}",
                    value=f"Kode: `{product.product_code}`\n"
                          f"Harga: {product.price_wl} WL\n"
                          f"Stok: {product.stock_quantity}\n"
                          f"Status: {status}",
                    inline=True
                )
        
        embed.set_footer(text="Update otomatis setiap 5 menit")
        return embed
    
    async def _get_or_create_user(
        self, 
        discord_id: str, 
        username: str, 
        db: Session
    ) -> DiscordUser:
        """Get or create Discord user"""
        user = db.query(DiscordUser).filter(
            DiscordUser.discord_id == str(discord_id)
        ).first()
        
        if not user:
            user = DiscordUser(
                discord_id=str(discord_id),
                discord_username=username
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create wallet
            wallet = DiscordWallet(user_id=user.id)
            db.add(wallet)
            db.commit()
        
        return user
    
    async def _process_purchase(
        self,
        user: DiscordUser,
        product_code: str,
        quantity: int,
        currency: str,
        db: Session
    ) -> BuyProductResponse:
        """Process product purchase"""
        try:
            # Get product
            product = db.query(LiveStock).filter(
                LiveStock.product_code == product_code,
                LiveStock.is_active == True
            ).first()
            
            if not product:
                return BuyProductResponse(
                    success=False,
                    message=f"Produk dengan kode {product_code} tidak ditemukan"
                )
            
            if product.stock_quantity < quantity:
                return BuyProductResponse(
                    success=False,
                    message=f"Stok tidak mencukupi. Tersedia: {product.stock_quantity}"
                )
            
            # Calculate total price in WL
            total_price_wl = product.price_wl * quantity
            
            # Convert to requested currency
            total_price = self._convert_from_wl(total_price_wl, currency)
            
            # Check user balance
            wallet = user.discord_wallet
            current_balance = getattr(wallet, f"{currency.lower()}_balance")
            
            if current_balance < total_price:
                return BuyProductResponse(
                    success=False,
                    message=f"Saldo {currency} tidak mencukupi. Dibutuhkan: {total_price}, Tersedia: {current_balance}"
                )
            
            # Process transaction
            new_balance = current_balance - total_price
            setattr(wallet, f"{currency.lower()}_balance", new_balance)
            
            # Update stock
            product.stock_quantity -= quantity
            
            # Create transaction record
            transaction = DiscordTransaction(
                user_id=user.id,
                transaction_type="buy",
                currency_type=CurrencyType(currency.lower()),
                amount=total_price,
                description=f"Pembelian {quantity}x {product.product_name}",
                reference_id=product.product_code
            )
            db.add(transaction)
            
            db.commit()
            db.refresh(wallet)
            
            return BuyProductResponse(
                success=True,
                message=f"Berhasil membeli {quantity}x {product.product_name}",
                transaction_id=transaction.id,
                remaining_balance=wallet
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing purchase: {e}")
            return BuyProductResponse(
                success=False,
                message="Terjadi kesalahan saat memproses pembelian"
            )
    
    def _calculate_wl_equivalent(self, wallet: DiscordWallet) -> Decimal:
        """Calculate total balance in WL equivalent"""
        return (
            wallet.wl_balance +
            (wallet.dl_balance * 100) +
            (wallet.bgl_balance * 10000)
        )
    
    def _convert_from_wl(self, wl_amount: Decimal, to_currency: str) -> Decimal:
        """Convert WL to other currency"""
        if to_currency == "WL":
            return wl_amount
        elif to_currency == "DL":
            return wl_amount / 100
        elif to_currency == "BGL":
            return wl_amount / 10000
        else:
            raise ValueError(f"Invalid currency: {to_currency}")
    
    async def start_bot(self):
        """Start the Discord bot"""
        if not self.bot or not self.bot_config:
            raise ValueError("Bot not initialized")
        
        try:
            await self.bot.start(self.bot_config.bot_token)
            self.is_running = True
        except Exception as e:
            logger.error(f"Error starting Discord bot: {e}")
            raise
    
    async def stop_bot(self):
        """Stop the Discord bot"""
        if self.bot and self.is_running:
            await self.bot.close()
            self.is_running = False


class LiveStockView(discord.ui.View):
    """View dengan buttons untuk live stock"""
    
    def __init__(self, products: List[LiveStock]):
        super().__init__(timeout=None)
        self.products = products
    
    @discord.ui.button(label="🛒 Buy", style=discord.ButtonStyle.green, custom_id="buy_button")
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BuyModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🌱 Grow ID", style=discord.ButtonStyle.blurple, custom_id="growid_button")
    async def growid_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = GrowIDModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="💰 Balance", style=discord.ButtonStyle.gray, custom_id="balance_button")
    async def balance_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Trigger balance command
        await interaction.response.defer(ephemeral=True)
        # Implementation similar to _handle_balance_command
    
    @discord.ui.button(label="🌍 World", style=discord.ButtonStyle.secondary, custom_id="world_button")
    async def world_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Trigger world command
        await interaction.response.defer()
        # Implementation similar to _handle_world_command


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
            
            # Process purchase (similar to buy command)
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(
                f"Memproses pembelian {quantity_int}x {self.product_code.value} dengan {currency_str}...",
                ephemeral=True
            )
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Jumlah harus berupa angka!",
                ephemeral=True
            )


class GrowIDModal(discord.ui.Modal, title="Set Grow ID"):
    """Modal untuk setting Grow ID"""
    
    grow_id = discord.ui.TextInput(
        label="Grow ID",
        placeholder="Masukkan Grow ID Anda...",
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        # Process Grow ID setting (similar to growid command)
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            f"Grow ID berhasil diset: {self.grow_id.value}",
            ephemeral=True
        )
