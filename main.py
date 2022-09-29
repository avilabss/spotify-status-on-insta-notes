import os
import time
import random
import traceback

from defaults import *
from helpers import *


username = config.get("credentials", "username")
password = config.get("credentials", "password")


try:
    client = InstaClient()

    if os.path.isfile(settings_file):
        client.load_settings(settings_file)

    client.login(username, password)
    client.get_timeline_feed()

    main_loop(client)

except TokenError:
    print("Token expired! Please create and update your token")

except ResponseError as e:
    print(e)
    print("There was an error in respone!")

except:
    traceback.print_exc()

finally:
    try:
        client.dump_settings(settings_file)
    except:
        pass
