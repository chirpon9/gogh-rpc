import os
import re

class LogParser:
    def __init__(self, parsed_data_callback):
        self.log_file_path = None
        self.file = None        
        self.last_position = 0    
        
        self.on_parsed_data = parsed_data_callback
        

        self.current_lobby_id = None
        self.lobby_members = set() 
        self.is_collecting_members = False 
        self.lobby_regex = re.compile(r"Joined Lobby: (\d+)")
        self.leave_regex = re.compile(r"LeaveRoom Called")
        self.member_regex = re.compile(r"Lobby Member: (\d+)")
        self.member_change_regex = re.compile(r"OnLobbyMemberListChanged Called")
        self.member_change_end_regex = re.compile(r"OnLobbyMemberListChanged End")
        

    def set_log_file(self, file_path):

        if self.file:
            self.file.close()
        
        self.current_lobby_id = None
        self.lobby_members.clear()
        self.is_collecting_members = False
        self.log_file_path = file_path
        print(f"Parser is now watching: {os.path.basename(file_path)}")
        
        try:
            self.file = open(self.log_file_path, 'r', encoding='utf-8')
            self.file.seek(0)
            self.last_position = 0
            self.read_new_lines()
            
        except Exception as e:
            self.file = None

    def read_new_lines(self):
        if not self.file:
            return

        self.file.seek(self.last_position)
        new_lines = self.file.readlines()
        self.last_position = self.file.tell()

        if not new_lines:
            return  # No new content


        state_changed = False
        
        for line in new_lines:
            join_match = self.lobby_regex.search(line)
            if join_match:
                new_lobby_id = join_match.group(1)
                if new_lobby_id != self.current_lobby_id:
                    self.current_lobby_id = new_lobby_id
                    self.lobby_members.clear()
                    self.is_collecting_members = True
                    state_changed = True
                continue
            
            member_match = self.member_regex.search(line)
            if member_match:
                if not self.is_collecting_members:
                    self.lobby_members.clear()
                    self.is_collecting_members = True
                steam_id = member_match.group(1)
                self.lobby_members.add(steam_id)
                continue
                
            leave_match = self.leave_regex.search(line)
            if leave_match:
                if self.current_lobby_id is not None:
                    self.current_lobby_id = None
                    self.lobby_members.clear()
                    self.is_collecting_members = False
                    state_changed = True
                continue
            
            member_change_end_match = self.member_change_end_regex.search(line)
            if member_change_end_match:
                if self.is_collecting_members:
                    self.is_collecting_members = False
                    state_changed = True
                continue
            
            if self.is_collecting_members:
                self.is_collecting_members = False
                state_changed = True
        

        if state_changed:
            player_count = len(self.lobby_members)
            self.on_parsed_data(self.current_lobby_id, player_count)


    def close(self):
        if self.file:
            print("Closing log file")
            self.file.close()
            self.file = None
