

import time, sys, argparse, signal
import client

args = argparse.ArgumentParser(
	description="Laika client example",
	epilog="You can use http://user:pass@host:port/path format for convenience",
)
args.add_argument("-e", "--env",  dest="environment", required=True,  help="Environment name")
args.add_argument("-u", "--user", dest="username",    required=False, help="Username")
args.add_argument("-p", "--pass", dest="password",    required=False, help="Password")
args.add_argument("url", help="URL for the laika")
parsed = args.parse_args()

sys.running = True

lk = client.Client(parsed.url, parsed.username, parsed.password, parsed.environment)
lk.init_timer(interval=5.0)

def interrupt_handler(signum, frame):
	print("quitting:", signum, frame)
	sys.running = False
	lk.stop()
	return

signal.signal(signal.SIGINT, interrupt_handler)

#send raw request using client
#re = client.request(method="POST", url="https://src.n0pe.me/", json=dict(hello="world"))

gen = lk.generator("hello")

while sys.running:
	time.sleep(1.0)
	print("generator", next(gen))

	print("envs:", lk.state.environments)
	print("features:", lk.state.features)
	print("hello(def)", lk.get_state("hello"))
	print("hello(def/ondemand)", lk.get_ondemand("hello"))
	print("hello(toggle/curl)", lk.feature_toggle("hello", "curl"))
	print("hello(curl)", lk.get_state("hello", "curl"))
	print("hello(curl/ondemand)", lk.get_ondemand("hello", "curl"))

	print("hello(set/True)", lk.set_state("hello", True))
	print("hello(get)", lk.get_state("hello"))
	print("hello(set/False)", lk.set_state("hello", False))
	print("hello(get)", lk.get_state("hello"))

	print(type(lk.get_features(named="hello")[0].created_at))
