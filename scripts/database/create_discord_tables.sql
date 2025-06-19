-- Create enum types
CREATE TYPE discordbotstatus AS ENUM ('ACTIVE', 'INACTIVE', 'MAINTENANCE');
CREATE TYPE currencytype AS ENUM ('wl', 'dl', 'bgl');

-- Create discord_bots table
CREATE TABLE discord_bots (
    id SERIAL PRIMARY KEY,
    bot_name VARCHAR(100) NOT NULL,
    bot_token TEXT NOT NULL,
    guild_id VARCHAR(50) NOT NULL,
    live_stock_channel_id VARCHAR(50),
    donation_webhook_url TEXT,
    status discordbotstatus NOT NULL DEFAULT 'INACTIVE',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_discord_bots_guild_id ON discord_bots (guild_id);
CREATE INDEX ix_discord_bots_id ON discord_bots (id);

-- Create discord_channels table
CREATE TABLE discord_channels (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER NOT NULL REFERENCES discord_bots(id) ON DELETE CASCADE,
    channel_id VARCHAR(50) NOT NULL,
    channel_name VARCHAR(100) NOT NULL,
    channel_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_discord_channels_id ON discord_channels (id);

-- Create discord_users table
CREATE TABLE discord_users (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) NOT NULL UNIQUE,
    discord_username VARCHAR(100) NOT NULL,
    grow_id VARCHAR(100),
    is_verified BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_discord_users_id ON discord_users (id);

-- Create discord_wallets table
CREATE TABLE discord_wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES discord_users(id) ON DELETE CASCADE,
    wl_balance NUMERIC(15,2) NOT NULL DEFAULT 0,
    dl_balance NUMERIC(15,2) NOT NULL DEFAULT 0,
    bgl_balance NUMERIC(15,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE (user_id)
);
CREATE INDEX ix_discord_wallets_id ON discord_wallets (id);

-- Create discord_transactions table
CREATE TABLE discord_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES discord_users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL,
    currency_type currencytype NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    description TEXT,
    reference_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_discord_transactions_id ON discord_transactions (id);

-- Create live_stocks table
CREATE TABLE live_stocks (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER NOT NULL REFERENCES discord_bots(id) ON DELETE CASCADE,
    product_code VARCHAR(100) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    price_wl NUMERIC(15,2) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    is_featured BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_live_stocks_id ON live_stocks (id);
CREATE INDEX ix_live_stocks_product_code ON live_stocks (product_code);

-- Create admin_world_configs table
CREATE TABLE admin_world_configs (
    id SERIAL PRIMARY KEY,
    world_name VARCHAR(100) NOT NULL,
    world_description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    access_level VARCHAR(50) NOT NULL DEFAULT 'public',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_admin_world_configs_id ON admin_world_configs (id);

-- Create discord_bot_configs table
CREATE TABLE discord_bot_configs (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    config_type VARCHAR(50) NOT NULL DEFAULT 'string',
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_discord_bot_configs_id ON discord_bot_configs (id);

-- Create discord_logs table
CREATE TABLE discord_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES discord_users(id) ON DELETE SET NULL,
    bot_id INTEGER NOT NULL REFERENCES discord_bots(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    action VARCHAR(50),
    channel_id VARCHAR(50),
    guild_id VARCHAR(50),
    error_details TEXT,
    extra_data TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_discord_logs_id ON discord_logs (id);

-- Create discord_commands table
CREATE TABLE discord_commands (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES discord_users(id) ON DELETE CASCADE,
    command_name VARCHAR(50) NOT NULL,
    command_args TEXT,
    channel_id VARCHAR(50) NOT NULL,
    guild_id VARCHAR(50) NOT NULL,
    success BOOLEAN NOT NULL DEFAULT true,
    execution_time FLOAT,
    error_message TEXT,
    response_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_discord_commands_id ON discord_commands (id);
