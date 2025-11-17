CREATE TABLE IF NOT EXISTS cars (
    id SERIAL PRIMARY KEY,
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    vin VARCHAR(17) UNIQUE NOT NULL,
    color VARCHAR(50),
    image_url TEXT,          -- ADD THIS
    thumbnail_url TEXT       -- ADD THIS
);

-- Add some sample data with images
INSERT INTO cars (make, model, year, price, vin, color) VALUES
('Toyota', 'Camry', 2023, 28000.00, '1HGCM82633A123456', 'Silver'),
('Honda', 'Civic', 2024, 25000.00, '2HGFC2F59MH123457', 'Blue'),
('Ford', 'Mustang', 2023, 45000.00, '1FA6P8TH5N5123458', 'Red')
ON CONFLICT (vin) DO NOTHING;