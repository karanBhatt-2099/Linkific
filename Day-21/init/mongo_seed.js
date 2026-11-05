db = db.getSiblingDB("shop");
db.products.insertMany([
  { sku: "P1", name: "Laptop",   price: 55000, category: "electronics" },
  { sku: "P2", name: "Headset",  price: 2500,  category: "electronics" },
  { sku: "P3", name: "Notebook", price: 120,   category: "stationery" }
]);
db.reviews.insertMany([
  { sku: "P1", rating: 5, comment: "Great" },
  { sku: "P2", rating: 4, comment: "Good sound" },
  { sku: "P3", rating: 3, comment: "Okay" }
]);
