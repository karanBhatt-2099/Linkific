"""Builds data/sales.db from 01_schema.sql plus deterministic synthetic data.
Also writes data/02_seed.sql so the data can be loaded in any SQL engine."""
import random, sqlite3, os, datetime as dt

random.seed(42)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "sales.db")
if os.path.exists(DB): os.remove(DB)

con = sqlite3.connect(DB)
con.executescript(open(os.path.join(ROOT, "data", "01_schema.sql")).read())

con.executemany("INSERT INTO regions VALUES (?,?)", [(1,"North"),(2,"South"),(3,"East"),(4,"West")])

employees = [
 (1,"Aisha Khan","CEO",None,1,250000),
 (2,"Rohan Mehta","VP Sales",1,1,180000),
 (3,"Priya Nair","VP Operations",1,2,175000),
 (4,"Karan Shah","Sales Manager",2,1,110000),
 (5,"Neha Rao","Sales Manager",2,3,108000),
 (6,"Vikram Singh","Sales Rep",4,1,70000),
 (7,"Sana Iyer","Sales Rep",4,2,72000),
 (8,"Arjun Das","Sales Rep",5,3,68000),
 (9,"Meera Joshi","Sales Rep",5,4,71000),
 (10,"Dev Patel","Ops Analyst",3,2,65000),
 (11,"Ira Bose","Ops Analyst",3,4,64000),
]
con.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?)", employees)

categories = [
 (1,"Electronics",None),(2,"Computers",1),(3,"Laptops",2),(4,"Accessories",2),
 (5,"Audio",1),(6,"Home",None),(7,"Kitchen",6),(8,"Furniture",6),(9,"Books",None),
]
con.executemany("INSERT INTO categories VALUES (?,?,?)", categories)

products = [
 (1,"Pro Laptop 14",3,1200,900),(2,"Air Laptop 13",3,950,700),(3,"Wireless Mouse",4,25,10),
 (4,"Mech Keyboard",4,90,45),(5,"USB-C Hub",4,45,20),(6,"Noise-Cancel Headphones",5,220,120),
 (7,"Bluetooth Speaker",5,80,40),(8,"Blender",7,70,35),(9,"Air Fryer",7,110,60),
 (10,"Coffee Maker",7,95,50),(11,"Office Chair",8,260,150),(12,"Standing Desk",8,480,300),
 (13,"SQL Cookbook",9,40,15),(14,"Data Design Book",9,55,20),(15,"Webcam HD",4,60,28),
 (16,"Smart Lamp",8,35,15),(17,"Gaming Monitor",2,330,220),(18,"Discontinued Gadget",1,20,12),
]
con.executemany("INSERT INTO products VALUES (?,?,?,?,?)", products)
price_of = {p[0]: p[3] for p in products}

first = ["Aarav","Diya","Ishaan","Kavya","Rahul","Sneha","Aditya","Pooja","Manish","Tara",
         "Nikhil","Anita","Sameer","Ritu","Yash","Divya","Harsh","Lata","Omkar","Zoya"]
last  = ["Sharma","Verma","Gupta","Reddy","Kulkarni","Menon","Chopra","Banerjee","Malhotra","Pillai"]
customers=[]
for cid in range(1,61):
    name=f"{random.choice(first)} {random.choice(last)}"
    signup=dt.date(2023,1,1)+dt.timedelta(days=random.randint(0,700))
    ref = random.choice([None]*3+list(range(1,cid))) if cid>1 else None
    customers.append((cid,name,f"user{cid}@example.com",random.randint(1,4),signup.isoformat(),ref))
con.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?)", customers)

reps=[6,7,8,9]
active_customers = list(range(1,56))      # customers 56-60 never order
sellable = list(range(1,18))              # product 18 never sells
oid=1; iid=1
start=dt.date(2024,1,1)
for _ in range(500):
    d = start+dt.timedelta(days=int(random.triangular(0,729,500)))
    cust=random.choice(active_customers)
    status=random.choices(["completed","cancelled","returned"],[88,7,5])[0]
    con.execute("INSERT INTO orders VALUES (?,?,?,?,?)",(oid,cust,random.choice(reps),d.isoformat(),status))
    for p in random.sample(sellable, random.randint(1,4)):
        con.execute("INSERT INTO order_items VALUES (?,?,?,?,?,?)",
                    (iid,oid,p,random.randint(1,3),price_of[p],random.choice([0,0,0,0.05,0.10,0.15])))
        iid+=1
    oid+=1
con.commit()

# Dump in FOREIGN-KEY DEPENDENCY ORDER (parents before children) so it loads into PostgreSQL/MySQL
ORDER = ["regions","employees","customers","categories","products","orders","order_items"]
with open(os.path.join(ROOT,"data","02_seed.sql"),"w") as f:
    for t in ORDER:
        cols = [r[1] for r in con.execute(f"PRAGMA table_info({t})")]
        pk = cols[0]
        for row in con.execute(f"SELECT * FROM {t} ORDER BY {pk}"):
            vals = ", ".join("NULL" if v is None else ("'" + v.replace("'", "''") + "'" if isinstance(v, str) else repr(v)) for v in row)
            f.write(f"INSERT INTO {t} VALUES ({vals});\n")
for t in ["regions","employees","customers","categories","products","orders","order_items"]:
    print(t, con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
