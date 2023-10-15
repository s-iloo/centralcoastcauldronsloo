create table
  public.potions (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    red integer null default 0,
    green integer null default 0,
    blue integer null default 0,
    dark integer null default 0,
    sku text null default 'NULL'::text,
    name text null default 'NULL'::text,
    quantity integer null default 0,
    price integer null default 0,
    constraint potions_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.carts (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    customer text null,
    constraint carts_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.cart_items (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    potion_id bigint null,
    cart_id bigint null,
    quantity integer null,
    constraint cart_items_pkey primary key (id),
    constraint cart_items_cart_id_fkey foreign key (cart_id) references carts (id),
    constraint cart_items_potion_id_fkey foreign key (potion_id) references potions (id)
  ) tablespace pg_default;