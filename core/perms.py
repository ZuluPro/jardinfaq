def user_can_add_plant(user):
    return user.is_administrator_or_moderator()


def user_can_validate(user):
    return user.reputation >= 500


def user_can_vote(user):
    return user.reputation >= 5
