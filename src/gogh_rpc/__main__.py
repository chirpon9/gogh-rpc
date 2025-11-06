from . import LogParser, start_file_watcher, PresenceUpdater

def main():
    presence = PresenceUpdater()
    parser = LogParser(parsed_data_callback=presence.update_lobby)
    presence.connect()
    
    if not presence.connected:
        return

    try:
        start_file_watcher(
            new_log_callback=parser.set_log_file,
            log_update_callback=parser.read_new_lines
        )
    except KeyboardInterrupt:
        pass
    finally:
        parser.close()
        presence.close()

if __name__ == "__main__":
    main()