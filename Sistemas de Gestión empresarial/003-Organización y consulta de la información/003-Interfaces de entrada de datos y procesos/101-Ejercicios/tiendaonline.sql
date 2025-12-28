-- =============================================
-- ONLINE SHOP DATABASE SCHEMA
-- =============================================

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS product_images;
DROP TABLE IF EXISTS product_reviews;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS brands;
DROP TABLE IF EXISTS payment_methods;
DROP TABLE IF EXISTS shipping_methods;
DROP TABLE IF EXISTS addresses;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS countries;
DROP TABLE IF EXISTS cities;
DROP TABLE IF EXISTS order_statuses;
DROP TABLE IF EXISTS payment_statuses;

-- =============================================
-- LOOKUP/REFERENCE TABLES
-- =============================================

-- Countries table
CREATE TABLE countries (
    country_id INT PRIMARY KEY AUTO_INCREMENT,
    country_name VARCHAR(100) NOT NULL UNIQUE,
    country_code CHAR(2) NOT NULL UNIQUE,
    phone_prefix VARCHAR(10)
);

-- Cities table
CREATE TABLE cities (
    city_id INT PRIMARY KEY AUTO_INCREMENT,
    city_name VARCHAR(100) NOT NULL,
    country_id INT NOT NULL,
    postal_code VARCHAR(20),
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    UNIQUE KEY unique_city_country (city_name, country_id)
);

-- Order statuses
CREATE TABLE order_statuses (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    status_name VARCHAR(50) NOT NULL UNIQUE,
    status_description VARCHAR(255)
);

-- Payment statuses
CREATE TABLE payment_statuses (
    payment_status_id INT PRIMARY KEY AUTO_INCREMENT,
    status_name VARCHAR(50) NOT NULL UNIQUE
);

-- Shipping methods
CREATE TABLE shipping_methods (
    shipping_method_id INT PRIMARY KEY AUTO_INCREMENT,
    method_name VARCHAR(100) NOT NULL UNIQUE,
    base_cost DECIMAL(10, 2) NOT NULL,
    estimated_days INT,
    description TEXT
);

-- Payment methods
CREATE TABLE payment_methods (
    payment_method_id INT PRIMARY KEY AUTO_INCREMENT,
    method_name VARCHAR(50) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Brands table
CREATE TABLE brands (
    brand_id INT PRIMARY KEY AUTO_INCREMENT,
    brand_name VARCHAR(100) NOT NULL UNIQUE,
    brand_description TEXT,
    website_url VARCHAR(255)
);

-- Categories table
CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    parent_category_id INT,
    category_description TEXT,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
);

-- =============================================
-- CUSTOMER RELATED TABLES
-- =============================================

-- Customers table
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Addresses table
CREATE TABLE addresses (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    address_type ENUM('billing', 'shipping', 'both') NOT NULL,
    street_address VARCHAR(255) NOT NULL,
    apartment VARCHAR(50),
    city_id INT NOT NULL,
    postal_code VARCHAR(20),
    is_default BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- =============================================
-- PRODUCT RELATED TABLES
-- =============================================

-- Products table
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) NOT NULL UNIQUE,
    category_id INT NOT NULL,
    brand_id INT,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    discount_percentage DECIMAL(5, 2) DEFAULT 0,
    stock_quantity INT NOT NULL DEFAULT 0,
    weight_kg DECIMAL(8, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (brand_id) REFERENCES brands(brand_id)
);

-- Product images table
CREATE TABLE product_images (
    image_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INT DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Product reviews table
CREATE TABLE product_reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_title VARCHAR(255),
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- =============================================
-- SHOPPING CART TABLES
-- =============================================

-- Cart items table
CREATE TABLE cart_items (
    cart_item_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY unique_customer_product (customer_id, product_id)
);

-- =============================================
-- ORDER RELATED TABLES
-- =============================================

-- Orders table
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_id INT NOT NULL,
    payment_status_id INT NOT NULL,
    payment_method_id INT NOT NULL,
    shipping_method_id INT NOT NULL,
    shipping_address_id INT NOT NULL,
    billing_address_id INT NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) NOT NULL,
    shipping_cost DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (status_id) REFERENCES order_statuses(status_id),
    FOREIGN KEY (payment_status_id) REFERENCES payment_statuses(payment_status_id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(payment_method_id),
    FOREIGN KEY (shipping_method_id) REFERENCES shipping_methods(shipping_method_id),
    FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id),
    FOREIGN KEY (billing_address_id) REFERENCES addresses(address_id)
);

-- Order items table
CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- =============================================
-- INSERT SAMPLE DATA
-- =============================================

-- Insert Countries
INSERT INTO countries (country_name, country_code, phone_prefix) VALUES
('Spain', 'ES', '+34'),
('United States', 'US', '+1'),
('United Kingdom', 'UK', '+44'),
('Germany', 'DE', '+49'),
('France', 'FR', '+33');

-- Insert Cities
INSERT INTO cities (city_name, country_id, postal_code) VALUES
('Madrid', 1, '28001'),
('Barcelona', 1, '08001'),
('New York', 2, '10001'),
('Los Angeles', 2, '90001'),
('London', 3, 'SW1A'),
('Berlin', 4, '10115'),
('Paris', 5, '75001');

-- Insert Order Statuses
INSERT INTO order_statuses (status_name, status_description) VALUES
('Pending', 'Order has been placed but not yet processed'),
('Processing', 'Order is being prepared'),
('Shipped', 'Order has been shipped'),
('Delivered', 'Order has been delivered'),
('Cancelled', 'Order has been cancelled'),
('Refunded', 'Order has been refunded');

-- Insert Payment Statuses
INSERT INTO payment_statuses (status_name) VALUES
('Pending'),
('Completed'),
('Failed'),
('Refunded');

-- Insert Shipping Methods
INSERT INTO shipping_methods (method_name, base_cost, estimated_days, description) VALUES
('Standard Shipping', 5.99, 7, 'Regular delivery within 5-7 business days'),
('Express Shipping', 14.99, 3, 'Fast delivery within 2-3 business days'),
('Overnight Shipping', 29.99, 1, 'Next day delivery'),
('Free Shipping', 0.00, 10, 'Free standard delivery for orders over $50');

-- Insert Payment Methods
INSERT INTO payment_methods (method_name, is_active) VALUES
('Credit Card', TRUE),
('Debit Card', TRUE),
('PayPal', TRUE),
('Apple Pay', TRUE),
('Google Pay', TRUE),
('Bank Transfer', TRUE);

-- Insert Brands
INSERT INTO brands (brand_name, brand_description, website_url) VALUES
('TechMaster', 'Leading electronics manufacturer', 'https://techmaster.example.com'),
('StyleWear', 'Fashion and apparel brand', 'https://stylewear.example.com'),
('HomeComfort', 'Home and living products', 'https://homecomfort.example.com'),
('SportPro', 'Sports and fitness equipment', 'https://sportpro.example.com'),
('BeautyGlow', 'Beauty and cosmetics', 'https://beautyglow.example.com');

-- Insert Categories
INSERT INTO categories (category_name, parent_category_id, category_description) VALUES
('Electronics', NULL, 'Electronic devices and accessories'),
('Clothing', NULL, 'Apparel and fashion items'),
('Home & Garden', NULL, 'Home improvement and garden supplies'),
('Sports & Outdoors', NULL, 'Sports equipment and outdoor gear'),
('Beauty & Health', NULL, 'Beauty products and health items'),
('Smartphones', 1, 'Mobile phones and accessories'),
('Laptops', 1, 'Laptop computers'),
('Men''s Clothing', 2, 'Clothing for men'),
('Women''s Clothing', 2, 'Clothing for women'),
('Furniture', 3, 'Home furniture');

-- Insert Customers
INSERT INTO customers (email, password_hash, first_name, last_name, phone, date_of_birth) VALUES
('john.doe@email.com', 'hash123abc', 'John', 'Doe', '+34600123456', '1985-03-15'),
('maria.garcia@email.com', 'hash456def', 'Maria', 'Garcia', '+34600234567', '1990-07-22'),
('james.smith@email.com', 'hash789ghi', 'James', 'Smith', '+1555123456', '1988-11-30'),
('sophie.martin@email.com', 'hash012jkl', 'Sophie', 'Martin', '+33612345678', '1992-05-18'),
('hans.mueller@email.com', 'hash345mno', 'Hans', 'Mueller', '+49151234567', '1987-09-25');

-- Insert Addresses
INSERT INTO addresses (customer_id, address_type, street_address, apartment, city_id, postal_code, is_default) VALUES
(1, 'both', 'Calle Gran Via 123', '3A', 1, '28013', TRUE),
(2, 'shipping', 'Paseo de Gracia 456', NULL, 2, '08007', TRUE),
(2, 'billing', 'Rambla Catalunya 789', '2B', 2, '08008', FALSE),
(3, 'both', '5th Avenue 789', 'Apt 12C', 3, '10022', TRUE),
(4, 'both', 'Champs-Élysées 101', NULL, 7, '75008', TRUE),
(5, 'both', 'Unter den Linden 55', NULL, 6, '10117', TRUE);

-- Insert Products
INSERT INTO products (product_name, sku, category_id, brand_id, description, price, discount_percentage, stock_quantity, weight_kg) VALUES
('TechMaster Smartphone X1', 'TM-SP-X1-001', 6, 1, 'Latest smartphone with 128GB storage and 5G connectivity', 699.99, 10, 50, 0.18),
('TechMaster Laptop Pro 15', 'TM-LP-PRO15-001', 7, 1, '15-inch laptop with Intel i7 processor and 16GB RAM', 1299.99, 15, 25, 2.1),
('StyleWear Men''s Cotton T-Shirt', 'SW-TS-MCT-BLU-M', 8, 2, 'Comfortable cotton t-shirt in blue - Medium size', 29.99, 0, 100, 0.2),
('StyleWear Women''s Summer Dress', 'SW-DR-WSD-RED-M', 9, 2, 'Elegant summer dress in red - Medium size', 79.99, 20, 45, 0.3),
('HomeComfort Office Chair', 'HC-CH-OFF-BLK', 10, 3, 'Ergonomic office chair with lumbar support', 249.99, 0, 30, 15.5),
('SportPro Running Shoes', 'SP-SH-RUN-BLK-42', 4, 4, 'Professional running shoes - Size 42', 119.99, 25, 60, 0.8),
('BeautyGlow Face Cream', 'BG-FC-HYD-50ML', 5, 5, 'Hydrating face cream 50ml', 49.99, 0, 150, 0.1),
('TechMaster Wireless Earbuds', 'TM-EB-WRL-001', 6, 1, 'Noise-cancelling wireless earbuds with charging case', 149.99, 5, 80, 0.05);

-- Insert Product Images
INSERT INTO product_images (product_id, image_url, is_primary, display_order) VALUES
(1, 'https://cdn.example.com/products/smartphone-x1-front.jpg', TRUE, 1),
(1, 'https://cdn.example.com/products/smartphone-x1-back.jpg', FALSE, 2),
(2, 'https://cdn.example.com/products/laptop-pro15-main.jpg', TRUE, 1),
(3, 'https://cdn.example.com/products/tshirt-blue-front.jpg', TRUE, 1),
(4, 'https://cdn.example.com/products/dress-red-front.jpg', TRUE, 1),
(5, 'https://cdn.example.com/products/office-chair-main.jpg', TRUE, 1),
(6, 'https://cdn.example.com/products/running-shoes-main.jpg', TRUE, 1),
(7, 'https://cdn.example.com/products/face-cream-main.jpg', TRUE, 1),
(8, 'https://cdn.example.com/products/earbuds-main.jpg', TRUE, 1);

-- Insert Product Reviews
INSERT INTO product_reviews (product_id, customer_id, rating, review_title, review_text, is_verified_purchase) VALUES
(1, 1, 5, 'Excellent phone!', 'Best smartphone I have ever owned. Fast, reliable, and great camera quality.', TRUE),
(1, 3, 4, 'Good but expensive', 'Great phone overall, but a bit pricey. Battery life could be better.', TRUE),
(2, 2, 5, 'Perfect for work', 'This laptop handles all my work tasks effortlessly. Highly recommend!', TRUE),
(3, 4, 5, 'Very comfortable', 'Great quality t-shirt, fits perfectly and the fabric is soft.', TRUE),
(6, 5, 4, 'Great running shoes', 'Comfortable and lightweight. Perfect for my daily runs.', TRUE);

-- Insert Cart Items
INSERT INTO cart_items (customer_id, product_id, quantity) VALUES
(1, 8, 1),
(1, 7, 2),
(3, 3, 3),
(5, 6, 1);

-- Insert Orders
INSERT INTO orders (customer_id, order_number, status_id, payment_status_id, payment_method_id, shipping_method_id, 
                   shipping_address_id, billing_address_id, subtotal, tax_amount, shipping_cost, discount_amount, total_amount) VALUES
(1, 'ORD-2024-001', 4, 2, 1, 2, 1, 1, 629.99, 132.30, 14.99, 70.00, 707.28),
(2, 'ORD-2024-002', 3, 2, 3, 1, 2, 3, 63.99, 13.44, 5.99, 16.00, 67.42),
(3, 'ORD-2024-003', 2, 2, 2, 3, 4, 4, 89.97, 18.89, 29.99, 0, 138.85),
(4, 'ORD-2024-004', 4, 2, 4, 1, 5, 5, 1299.99, 273.00, 0.00, 194.99, 1378.00),
(5, 'ORD-2024-005', 1, 1, 1, 1, 6, 6, 89.99, 18.90, 5.99, 30.00, 84.88);

-- Insert Order Items
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_amount, total_price) VALUES
(1, 1, 1, 699.99, 70.00, 629.99),
(2, 4, 1, 79.99, 16.00, 63.99),
(3, 3, 3, 29.99, 0, 89.97),
(4, 2, 1, 1299.99, 194.99, 1105.00),
(5, 6, 1, 119.99, 30.00, 89.99);

-- =============================================
-- USEFUL QUERIES
-- =============================================

-- Show all products with their categories and brands
SELECT 
    p.product_name,
    p.sku,
    c.category_name,
    b.brand_name,
    p.price,
    p.stock_quantity
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN brands b ON p.brand_id = b.brand_id;

-- Show customer orders with details
SELECT 
    o.order_number,
    CONCAT(cu.first_name, ' ', cu.last_name) AS customer_name,
    o.order_date,
    os.status_name,
    o.total_amount
FROM orders o
JOIN customers cu ON o.customer_id = cu.customer_id
JOIN order_statuses os ON o.status_id = os.status_id
ORDER BY o.order_date DESC;
