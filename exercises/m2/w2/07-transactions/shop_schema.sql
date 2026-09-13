-- Provided schema for the transaction exercise. Loaded by the tests.
CREATE TABLE products (
    id     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name   text   NOT NULL,
    price  bigint NOT NULL CHECK (price > 0),
    stock  integer NOT NULL CHECK (stock >= 0)
);

CREATE TABLE orders (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     bigint NOT NULL,
    total       bigint NOT NULL CHECK (total >= 0),
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE order_items (
    order_id    bigint  NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    product_id  bigint  NOT NULL REFERENCES products (id),
    quantity    integer NOT NULL CHECK (quantity > 0),
    unit_price  bigint  NOT NULL,           -- snapshot of the price at purchase time
    PRIMARY KEY (order_id, product_id)
);
CREATE INDEX order_items_product_id_idx ON order_items (product_id);
