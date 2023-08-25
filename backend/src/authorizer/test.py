import time
from ratelimiter import *


while True:
    time.sleep(1)
    print('pushing') 
    push_retweet('user_id', 3)
    push_like('user_id', 4)
