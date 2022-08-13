import RobloxRequest 

#very basic function to detect bots, you can rewrite this and use a more efficient method
def is_bot(follower):
    url = "friends.roblox.com/v1/users/"+str(follower.id)+"/{}/count"
    followings_num = RobloxRequest.request("GET", url.format("followings"), to_json=True).count
    friends_num = RobloxRequest.request("GET", url.format("friends"), to_json=True).count 
    return followings_num == 0 and friends_num == 0

def sanitize_input(prompt):
    return input(prompt+" ").lower().replace(" ", "")

def ask(prompt):
    response = sanitize_input(prompt)
    while response != "no" and response != "yes":
        print("Invalid response!")
        response = sanitize_input(prompt) 
    return response == "yes"

def pin_locked():
    return RobloxRequest.request("GET", "auth.roblox.com/v1/account/pin", True, to_json=True).isEnabled 

def check_pin_status():
    while True:
        response = ask("Continue? yes/no")
        if response:
            if pin_locked(): print("You must disable your account pin before continuing")
            else: break 
        else: exit()

def set_block_status(id, status):
    method = status and "block" or "unblock"
    return RobloxRequest.request("POST", f"accountsettings.roblox.com/v1/users/{id}/{method}", True, True)

def remove_follower(follower):
    blocked = set_block_status(follower.id, True) 
    set_block_status(follower.id, False) 
    return blocked != False 

def remove_followers(followers, failed):
    for follower in followers:
        success = remove_follower(follower) 
        if success:
            print(f"Removed follower: {follower.name}")
        else:
            print(f"REMOVAL FAILED: {follower.name}") 
            failed.append(follower) 

def remove_failed_attempts(failed):
    new = [] 
    if len(failed) > 0:
        response = ask(f"{len(failed)} followers failed to delete, retry? yes/no")
        if response:
            remove_followers(failed, new) 
            remove_failed_attempts(new) 

def main():
    RobloxRequest.set_cookie(input("Cookie: "))
    user_info = RobloxRequest.request("GET", "users.roblox.com/v1/users/authenticated", True, to_json=True) 
    print(f"Authenticated as {user_info.name}")
    check_pin_status()
    only_bots = ask("Only remove bots? yes/no")
    RobloxRequest.update_csrf()
    cursor = ""
    failed = [] 
    while cursor != None:
        result = RobloxRequest.request("GET", f"friends.roblox.com/v1/users/{user_info.id}/followers?cursor={cursor}", to_json=True)
        filtered = [] 
        for follower in result.data:
            if only_bots and is_bot(follower) or not only_bots: filtered.append(follower) 
        remove_followers(filtered, failed) 
        cursor = result.nextPageCursor 
    remove_failed_attempts(failed) 
    print("Script execution finished")

if __name__ == "__main__":
    main()
