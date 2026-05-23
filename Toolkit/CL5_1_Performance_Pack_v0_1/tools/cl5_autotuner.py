from dataclasses import dataclass
@dataclass
class Profile: shard_kib:int; concurrency_k:int; http3_streams:int; energy_mode:str
def choose_profile(bandwidth_mbps: float, rtt_ms: float, pref: str="balanced") -> Profile:
    if rtt_ms <= 20: shard, K = 512, (32 if bandwidth_mbps<50 else 48)
    elif rtt_ms <= 80: shard, K = 512, (48 if bandwidth_mbps<50 else 64)
    elif rtt_ms <= 180: shard, K = 256, (64 if bandwidth_mbps>=20 else 48)
    else: shard, K = 256, (32 if bandwidth_mbps<20 else 48)
    streams = K; mode = "turbo" if pref=="speed" else ("eco" if pref=="eco" else ("turbo" if K>=48 else "eco"))
    return Profile(shard, K, streams, mode)
