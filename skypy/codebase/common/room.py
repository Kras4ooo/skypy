class Room:
    def __init__(self):
        self.room_id = None
        self.members = []

    @staticmethod
    def check_is_exist_room(room_uid, rooms):
        if room_uid in rooms:
            return True
        return False
