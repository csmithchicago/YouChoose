-- Save product names to text file to be used by spaCy
COPY(
SELECT product_name
FROM products
)
TO '/home/coreys/perm-usb/coreys/Documents/instacart/analyze_instacart_data/data/interim/products_sold.txt';