CREATE TABLE IF NOT EXISTS cars (
    id SERIAL PRIMARY KEY,
    make VARCHAR NOT NULL,
    model VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    price FLOAT NOT NULL,
    vin VARCHAR UNIQUE NOT NULL,
    color VARCHAR
);

-- Sample data
INSERT INTO cars (make, model, year, price, vin, color) VALUES
('Toyota', 'Camry', 2023, 28999.99, '4T1BF1FK0DU123456', 'Silver'),
('Honda', 'Civic', 2022, 24999.99, '2HGFC2F69KH654321', 'Blue')
ON CONFLICT DO NOTHING;