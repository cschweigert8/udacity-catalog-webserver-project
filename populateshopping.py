from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbsetup import Category, Base, CategoryItem, User

engine = create_engine('sqlite:///shoppingcart.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = User(name="admin", email="admin@admin.com")
session.add(user1)
session.commit()

# Shopping options for hiking 
category1 = Category(catName="Hiking")

session.add(category1)
session.commit()

catItem1 = CategoryItem(itemName="Hiking Boots", description="Comfy, stable, weatherproof, hiking boots for all of your adventures!",
                     price="$99.50", category=category1, user=user1)

session.add(catItem1)
session.commit()


catItem2 = CategoryItem(itemName="All-weather Pants", description="Durable pants that zip off to shorts to keep you comfortable in any weather situation.",
                     price="$49.99", category=category1, user=user1)

session.add(catItem2)
session.commit()

catItem3 = CategoryItem(itemName="Hat", description="Keep the sun off your face!",
                     price="$10.99", category=category1, user=user1)

session.add(catItem3)
session.commit()

# Shopping options for camping 
category2 = Category(catName="Camping")

session.add(category2)
session.commit()

catItem1 = CategoryItem(itemName="Tent", description="A safe, warm place for you to sleep!",
                     price="$87.50", category=category2, user=user1)

session.add(catItem1)
session.commit()

catItem2 = CategoryItem(itemName="Jet Boil", description="Jet Boil heats up water in seconds for your coffee, tea, or food!",
                     price="$79.47", category=category2, user=user1)

session.add(catItem2)
session.commit()


# Shopping options for off roading
category3 = Category(catName="Off Roading")

session.add(category3)
session.commit()


catItem1 = CategoryItem(itemName="Off Road Lights", description="Bright off road lights help you see even in the darkest of nights.",
                     price="$200.50", category=category3, user=user1)

session.add(catItem1)
session.commit()

catItem2 = CategoryItem(itemName="Wench", description="Stuck in the mud? Worry no more! This wench will get you out.",
                     price="$239.99", category=category3, user=user1)

session.add(catItem2)
session.commit()

catItem3 = CategoryItem(itemName="Bumper", description="Are you a terrible driver? Do you hit a lot of trees? Slap this bumper on to protect you.",
                     price="$549.99", category=category3, user=user1)

session.add(catItem3)
session.commit()