from pypresence import Presence
import time

CLIENT_ID = "1435313077401813022"

class PresenceUpdater:

    
    def __init__(self):
        self.rpc = None
        self.connected = False
        self.current_lobby_id = None

    def connect(self):
        try:
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.connected = True
            self.current_lobby_id = "INITIAL"
            self.update_lobby(None, 0) 
        except Exception as e:
            self.connected = False

    def update_lobby(self, lobby_id, player_count):
        if not self.connected:
            return
        if lobby_id == self.current_lobby_id:
            return
        
        self.current_lobby_id = lobby_id

        try:
            if lobby_id:
                details_text = f"{lobby_id}"
                state_text = f"In a room with {player_count - 1} others"
                self.rpc.update(
                    large_image ="gogh",
                    name = "gogh: Focus with Your Avatar",
                    state=details_text,
                    details=state_text,
                    
                )
            else:
                self.rpc.update(
                    large_image="gogh",
                    name = "gogh: Focus with Your Avatar",
                    state="In own room"
                )

        except Exception as e:
            self.connected = False

    def close(self):
        if self.connected and self.rpc:
            self.rpc.close()