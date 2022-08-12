import RobloxRequest 

def sanitize_input(prompt):
    return input(prompt).lower().replace(" ", "")

def ask(prompt):
    response = sanitize_input(prompt)
    while response != "no" and response != "yes":
        print("Invalid response!")
        response = sanitize_input(prompt) 
    return response == "yes"

def set_block_status(id, status):
    url = "accountsettings.roblox.com/v1/users/{}/{}"
    method = status and "block" or "unblock"
    return RobloxRequest.request("POST", url.format(id, method), True, True)

def remove_follower(follower):
    blocked = set_block_status(follower.id, True) 
    set_block_status(follower.id, False) 
    return blocked != False 

#very basic function to detect bots, you can rewrite this and use a more efficient method
def is_bot(follower):
    url_format = "friends.roblox.com/v1/users/{}/{}/count"
    followings_num = RobloxRequest.request("GET", url_format.format(follower.id, "followings"), to_json=True).count
    friends_num = RobloxRequest.request("GET", url_format.format(follower.id, "friends"), to_json=True).count 
    return followings_num == 0 and friends_num == 0

def main():
    RobloxRequest.set_cookie(input("Cookie: "))
    user_info = RobloxRequest.request("GET", "users.roblox.com/v1/users/authenticated", True, to_json=True) 
    print("Authenticated as", user_info.name)
    if not ask("Continue? yes/no "): exit() 
    only_bots = ask("Only unfollow bots? yes/no ")
    url_format = "friends.roblox.com/v1/users/{}/followers?cursor={}"
    cursor = ""
    RobloxRequest.update_csrf()
    while True:
        result = RobloxRequest.request("GET", url_format.format(user_info.id, cursor), to_json=True)
        cursor = result.nextPageCursor 
        for follower in result.data:
            if only_bots and is_bot(follower) or not only_bots:
                success = remove_follower(follower)
                if success:
                    print("Removed follower:", follower.name)
                else:
                    print("REMOVAL FAILED:", follower.name) 
        if cursor == None: break 
    print("Script execution finished")

if __name__ == "__main__":
    main()
