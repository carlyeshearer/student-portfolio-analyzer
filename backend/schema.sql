-- Author: Carly Shearer
-- Purpose: Database stores the following...
    -- user portfolios
    -- holdings for each portfolio
    -- user goals for each portfolio
    -- static information about etf holdings

drop table if exists holdings;
drop table if exists etf_holdings;
drop table if exists goals;
drop table if exists portfolios;

create table portfolios (
    id integer primary key,
    name string not null
);

create table holdings (
    id integer primary key,
    portfolio_id integer not null,
    ticker text not null, --ticker for ETFs, name/ID for other accounts
    asset_type text not null, --support ETFs, stocks crypto, CDs, savings, bonds, cash
    value real not null,
    apy real, --assets with interest
    maturity_date string --CDs and bonds
);

create table goals (
    id integer primary key,
    portfolio_id integer not null,
    description string not null,
    time_horizon_years integer not null,
    risk_tolerance string not null,
    foreign key (portfolio_id) references portfolios(id)
);

create table etf_holdings (
    id integer primary key,
    etf_ticker string not null,
    holding_ticker string not null,
    weight real not null
);

-- static information about composition of ETFs for comparison

insert into etf_holdings
    (etf_ticker, holding_ticker, weight)
values
    ('VOO', 'AAPL', 7.0),
    ('VOO', 'MSFT', 6.5),
    ('VOO', 'NVDA', 6.0),
    ('VOO', 'AMZN', 3.5),
    ('QQQ', 'AAPL', 9.0),
    ('QQQ', 'MSFT', 8.5),
    ('QQQ', 'NVDA', 8.0),
    ('QQQ', 'AMZN', 5.0);