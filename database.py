from tinydb import TinyDB, Query

# Initialize the database
db = TinyDB('users.json')
User = Query()

def add_user(user_id):
    """
    Add a new user to the database.
    If the user already exists, no action is taken.
    """
    try:
        if not db.contains(User.id == user_id):
            db.insert({'id': user_id, 'balance': 0, 'referrals': [], 'blocked': False})
    except Exception as e:
        print(f"Error adding user {user_id}: {e}")

def update_balance(user_id, amount):
    """
    Update the user's balance by adding or subtracting the specified amount.
    """
    try:
        if db.contains(User.id == user_id):
            current_balance = db.get(User.id == user_id)['balance']
            db.update({'balance': current_balance + amount}, User.id == user_id)
    except Exception as e:
        print(f"Error updating balance for user {user_id}: {e}")

def get_balance(user_id):
    """
    Retrieve the current balance of the user.
    Returns 0 if the user does not exist.
    """
    try:
        user = db.get(User.id == user_id)
        return user['balance'] if user else 0
    except Exception as e:
        print(f"Error getting balance for user {user_id}: {e}")
        return 0

def add_referral(user_id, referral_id):
    """
    Add a referral to the user's list of referrals.
    If the referral is new, the user earns 10 Fox TOKEN.
    """
    try:
        if db.contains(User.id == user_id):
            user_data = db.get(User.id == user_id)
            referrals = user_data['referrals']
            if referral_id not in referrals:
                referrals.append(referral_id)
                db.update({'referrals': referrals}, User.id == user_id)
                update_balance(user_id, 10)  # Add 10 tokens to the user's balance
    except Exception as e:
        print(f"Error adding referral for user {user_id}: {e}")

def block_user(user_id):
    """
    Mark a user as blocked in the database.
    """
    try:
        if db.contains(User.id == user_id):
            db.update({'blocked': True}, User.id == user_id)
    except Exception as e:
        print(f"Error blocking user {user_id}: {e}")

def unblock_user(user_id):
    """
    Mark a user as unblocked in the database.
    """
    try:
        if db.contains(User.id == user_id):
            db.update({'blocked': False}, User.id == user_id)
    except Exception as e:
        print(f"Error unblocking user {user_id}: {e}")

def get_users_count():
    """
    Return the total number of users in the database.
    """
    try:
        return len(db)
    except Exception as e:
        print(f"Error getting total users count: {e}")
        return 0

def get_blocked_users_count():
    """
    Return the number of users marked as blocked.
    """
    try:
        return len(db.search(User.blocked == True))
    except Exception as e:
        print(f"Error getting blocked users count: {e}")
        return 0

def get_all_users():
    """
    Return a list of IDs of all users in the database.
    """
    try:
        return [user['id'] for user in db.all()]
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []