from app import db, User

# Make sure tables exist
db.create_all()

# Query all users
users = User.query.all()
if users:
    for user in users:
        print(user.to_dict())
else:
    print("No users found in the database.")

